import json
import boto3
import redis
import numpy as np
from redis.commands.search.query import Query

# === Setup ===
secretsmanager = boto3.client("secretsmanager", region_name="eu-west-1")
def get_secrets(secret_name):
    try:
        response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response['SecretString'])
        return secret_dict
    except Exception as e:
        print(f"? Failed to retrieve {secret_name} credentials: {e}")
        raise

secret =  get_secrets("dev/python/api")
REDIS_HOST = secret["REDIS_HOST"]
REDIS_PORT = secret["REDIS_PORT"]
REDIS_USER = secret["REDIS_USER"]
REDIS_PASS = secret["REDIS_PASS"]
REDIS_INDEX = "page_index"
VECTOR_DIM = 1024
TOP_K = 2

redis_conn = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USER,
    password=REDIS_PASS,
    decode_responses=True
)

bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")

# === Embedding ===
def generate_embedding_titan_embed(text: str):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text})
    )
    raw = response['body'].read()
    data = json.loads(raw)
    embedding = data.get("embedding")
    if embedding is None:
        raise Exception("No embedding returned from Titan")
    return embedding

# === Redis Vector Search ===
def search_redis_vector(query_embedding):
    base_query = f'*=>[KNN {TOP_K} @embedding $vec AS vector_score]'
    q = Query(base_query).sort_by("vector_score").return_fields("page_name", "vector_score", "text").dialect(2)
    vector_bytes = np.array(query_embedding, dtype=np.float32).tobytes()
    results = redis_conn.ft(REDIS_INDEX).search(q, query_params={"vec": vector_bytes})

    SCORE_THRESHOLD = 0.4
    docs = []
    for doc in results.docs:
        score = float(doc.vector_score)
        if score > SCORE_THRESHOLD:
            docs.append({"page_name": doc.page_name, "score": score, "vector_score": score,"text": getattr(doc, "text", "")})
            print(f"Found doc: {doc.page_name} with score: {score}")
    return docs

# === Claude Relevance Check ===
def semantic_relevance_check(question: str, context: str) -> bool:
    print(f"?? **** Context: {context}")
    prompt = (
        f"Question: \"{question}\"\n"
        f"Context: \"{context}\"\n"
        f"Is the question relevant to the context? Answer yes or no."
    )
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.2
            })
        )
        raw_output = response['body'].read()
        output = json.loads(raw_output)
        content = output['content'][0]['text'].strip().lower()
        print(f"?? Claude relevance check: {content}")
        return content.startswith("yes")
    except Exception as e:
        print(f"? Relevance check failed: {e}")
        return False

# === Claude Answer Generation ===
def generate_answer(question, context_docs):
    #context_text = "\n\n".join([f"Page: {doc['page_name']}" for doc in context_docs])
    context_text = "\n\n".join([
    f"Page: {doc['page_name']}\nContext: {doc.get('text', '')}"
    for doc in context_docs
    ])

    prompt = f"Given the following context:\n{context_text}\n\nAnswer this question: {question}"
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000
            })
        )
        raw_output = response['body'].read()
        output = json.loads(raw_output)
        content = output['content'][0]['text']
        return content
    except Exception as e:
        print(f"\n? Claude processing failed: {e}")
        return "An error occurred while generating the answer."

# === Polish Claude Response ===
def polish_answer(raw_answer, docs):
    if not docs:
        return "? Sorry, I could not find anything relevant to your question."
    lines = raw_answer.strip().split("\n")
    main_lines = [line for line in lines if "likely" in line or "you would need to look" in line]
    if main_lines:
        return main_lines[-1].strip()
    return raw_answer.strip()

# === Lambda Handler ===
def lambda_handler(event, context):
    try:
        query_text = event.get("query") or event["queryStringParameters"]["query"]
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Query parameter missing"
            })
        }

    print(f"Received query: {query_text}")

    # Step 1: Generate embedding using Titan model
    query_embedding = generate_embedding_titan_embed(query_text)
    print("? Query embedded")

    # Step 2: Vector search from Redis
    docs = search_redis_vector(query_embedding)
    print(f"? Found {len(docs)} docs")

    # Step 3: No results case
    if not docs:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "human": query_text,
                "bot": "? Sorry, I could not find anything relevant to your question.",
                "retrieved_docs": [],
                "confidence": 0.0,
                "follow_up": "Would you like to rephrase or ask something else?"
            })
        }

    # Step 4: Semantic relevance check with Claude
    print(f" This is I am getting from Redis:::::{docs}")
    top_doc = docs[0]
    #context_summary = f"Page: {top_doc.get('page_name', '')}"
    #context_summary = f"Page: {top_doc['page_name']}\nSnippet:\n{top_doc['chunk']}"
    # Use snippet only if available; else just page name
    snippet = top_doc.get("chunk") or top_doc.get("text") or ""
    context_summary = f"Page: {top_doc['page_name']}\nSnippet:\n{snippet}" if snippet else f"Page: {top_doc['page_name']}"
    is_relevant = semantic_relevance_check(query_text, context_summary)

    if not is_relevant :
        print("?? Irrelevant query (detected by Claude)")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "human": query_text,
                "bot": "? Sorry, I could not find anything relevant to your question.",
                "retrieved_docs": [],
                "confidence": 0.0,
                "follow_up": "Would you like to ask something else related to JSP or UI?"
            })
        }

    # Step 5: Generate and polish answer
    raw_answer = generate_answer(query_text, docs)
    polished = polish_answer(raw_answer, docs)
    confidence = round(1 - float(top_doc.get('vector_score', 0.5)), 2)

    # Step 6: Return final structured response
    return {
        "statusCode": 200,
        "body": json.dumps({
            "human": query_text,
            "bot": polished,
            "retrieved_docs": docs,
            "confidence": confidence,
            "follow_up": "Do you want to know more about that JSP or a relevant question?"
        })
    }

