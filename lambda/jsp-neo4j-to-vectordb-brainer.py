# Author : Rajat and created open-source by Rajat on 2024-03-08
# This code is part of a project to analyze JSP files using AWS Bedrock and store the results in a Neo4j graph database.
# Its again one time or incremental run to extract data from JSP files in an S3 bucket and store it in Neo4j.

import json
import time
import boto3
from neo4j import GraphDatabase
import redis
import numpy as np
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition,IndexType
from redis.commands.search.query import Query

# === Configs ===
secretsmanager = boto3.client("secretsmanager", region_name="eu-west-1")
def get_secrets(secret_name):
    try:
        response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response['SecretString'])
        return secret_dict
    except Exception as e:
        print(f"Failed to retrieve {secret_name} credentials: {e}")
        raise

secret =  get_secrets("dev/python/api")
# Neo4j connection
NEO4J_URI = secret["NEO4J_URI"]
NEO4J_USER =  secret["NEO4J_USER"]
NEO4J_PASSWORD = secret["NEO4J_PASSWORD"]
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Bedrock client (Claude / Titan embedding)
bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")

# Redis connection
redis_conn = redis.Redis(
    host=secret["REDIS_HOST"],
    port=secret["REDIS_PORT"],
    username= secret["REDIS_USER"],
    decode_responses=True,
    password=  secret["REDIS_PASS"]
)

REDIS_INDEX_NAME = "page_index"
REDIS_VECTOR_DIM = 1024

# === Redis Upsert ===
def create_redis_index():
    try:
        redis_conn.ft(REDIS_INDEX_NAME).create_index(
            fields=[
                TextField("page_name"),
                TextField("text"),  
                VectorField("embedding", "FLAT", {
                    "TYPE": "FLOAT32",
                    "DIM": REDIS_VECTOR_DIM,
                    "DISTANCE_METRIC": "COSINE"
                })
            ],
            definition=IndexDefinition(prefix=["doc:"], index_type=IndexType.HASH)
        )
        print("Redis vector index created.")
    except Exception as e:
        print(f"Redis index may already exist or failed: {e}")


def upsert_to_redis(doc_id: str, embedding: list[float], metadata: dict):
    key = f"doc:{doc_id}"
    vector_bytes = np.array(embedding, dtype=np.float32).tobytes()

    #  Prepare plain text summary (fields + actions + relationships)
    fields_text = f"Fields: {', '.join(metadata.get('fields', []))}"
    actions_text = f"Actions: {', '.join(metadata.get('actions', []))}"
    relationship_list = [
        f"{r['from']} -[{r['relation']}]-> {r['to']}"
        for r in metadata.get('relationships', [])
    ]
    relationships_text = f"Relationships: {', '.join(relationship_list)}"
    flat_text = f"{fields_text}\n{actions_text}\n{relationships_text}"

    #  HSET command (note the use of commas, not colons!)
    redis_conn.execute_command(
        "HSET", key,
        "embedding", vector_bytes,
        "page_name", metadata["page_name"],
        "text", flat_text
    )

    print(f" Upserted doc_id: {doc_id} into Redis")



    # Store vector, page_name, and contextual text
    redis_conn.execute_command(
        "HSET", key,
        "embedding", vector_bytes,
        "page_name", metadata["page_name"],
        "text", flat_text  #  ADDED: context used later in retrieval
    )
    print(f" Upserted doc_id: {doc_id} into Redis")


# === Titan Embedding ===
def generate_embedding(text: str, retries=3) -> list[float]:
    model_id = "amazon.titan-embed-text-v2:0"
    
    for attempt in range(retries):
        try:
            print("Invoking Titan...")
            response = bedrock.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({"inputText": text})
            )
            raw_output = response['body'].read()
            print(" Raw Bedrock response received.")
            print("🔍 Calling Bedrock model:", model_id)
            
            result = json.loads(raw_output)
            embedding = result.get("embedding")
            print(f" Embedding length: {len(embedding)}")
            print(f" Byte size: {len(embedding) * 4}")
            return embedding

        except Exception as e:
            print(f" Titan embedding failed (attempt {attempt+1}): {e}")
            time.sleep(1)

    raise Exception("Titan embedding failed after retries")


# === Neo4j Fetch ===
def fetch_all_pages_from_neo4j(tx):
    query = """
        MATCH (p:Page)
        OPTIONAL MATCH (p)-[:HAS_FIELD]->(f:Field)
        OPTIONAL MATCH (p)-[:SUPPORTS_ACTION]->(a:Action)
        OPTIONAL MATCH (e1:Entity)-[r:RELATED]->(e2:Entity)
        RETURN
        coalesce(p.jsp_name, p.name) AS page_name,
        collect(DISTINCT f.name) AS fields,
        collect(DISTINCT a.name) AS actions,
        collect(DISTINCT {from: e1.name, to: e2.name, relation: r.type}) AS relationships,
        elementId(p) AS page_id
    """
    result = tx.run(query)
    return [record.data() for record in result]


# === Main Lambda Handler ===
def lambda_handler(event, context):
    total_docs_upserted = 0
    print("-----------------START-----------------------")

    # Redis index
    create_redis_index()

    with neo4j_driver.session() as session:
        pages = session.read_transaction(fetch_all_pages_from_neo4j)
        print("-----------------Neo4j connected and fetched records-----------------------")

        for page in pages:
            page_name = page.get("page_name", "UnknownPage")
            page_id = page.get("page_id")
            doc_id = str(page_id)

            # Prepare text for embedding
            text_for_embedding = json.dumps({
                "page_name": page_name,
                "fields": page.get("fields", []),
                "actions": page.get("actions", []),
                "relationships": page.get("relationships", [])
            })

            try:
                embedding_vector = generate_embedding(text_for_embedding)
                print("🧪 Embedding length:", len(embedding_vector))  # Should be 1536

                vector_bytes = np.array(embedding_vector, dtype=np.float32).tobytes()
                print("📦 Byte size:", len(vector_bytes))  # Should be 6144
                # 🧪 Embedding length: 1024
                # 📦 Byte size: 4096
            except Exception as e:
                print(f" Embedding generation failed for page {page_name}: {e}")
                continue

            metadata = {
                "page_name": page_name,
                "fields": page.get("fields", []),
                "actions": page.get("actions", []),
                "relationships": page.get("relationships", []),
                "neo4j_page_id": page_id
            }

            try:
                upsert_to_redis(doc_id, embedding_vector, metadata)
                total_docs_upserted += 1
            except Exception as e:
                print(f" Redis upsert failed for page {page_name}: {e}")
                continue

    neo4j_driver.close()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Upserted {total_docs_upserted} documents into Redis vector index."
        })
    }
