import json
import boto3
from neo4j import GraphDatabase


secretsmanager = boto3.client("secretsmanager", region_name="eu-west-1")
def get_secrets(secret_name):
    try:
        response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response['SecretString'])
        return secret_dict
    except Exception as e:
        print(f"❌ Failed to retrieve {secret_name} credentials: {e}")
        raise




# === AWS Setup ===
s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")

secret = get_secrets("dev/python/api")
NEO4J_URI = secret["NEO4J_URI"]
NEO4J_USER = secret["NEO4J_USER"]
NEO4J_PASSWORD = secret["NEO4J_PASSWORD"]

neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# === HARDCODED S3 LOCATION ===
BUCKET_NAME = "jsp-legacy-codes"
JSP_PREFIX = ""  # Keep empty since JSPs are directly under root



def lambda_handler(event, context):
    print("=== 🚀 Lambda triggered! ===")
    # List all JSPs in the specified S3 prefix
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=JSP_PREFIX)
    if "Contents" not in response:
        return {"statusCode": 404, "body": "No JSPs found in the bucket."}

    for obj in response["Contents"]:
        key = obj["Key"]

        if not key.endswith(".jsp"):
            continue  # Skip non-JSP files (safe filter)

        if key not in ["beneficiaryAdd.jsp", "fundTransfer.jsp","claimRequest.jsp"]:
            continue  # ⏩ Skip all other JSPs for this test

        print(f"\n=== 📄 Processing JSP: {key} ===")

        # Read the JSP file content from S3
        jsp_code = s3.get_object(Bucket=BUCKET_NAME, Key=key)['Body'].read().decode("utf-8")

        # === Claude Prompt Template ===
        prompt = f"""  # ✅ Updated (improved formatting and clarity)
You are a Legacy JSP Page Analyst for an Insurance company.Output ONLY the JSON in exact format. Do NOT add explanations or any other text.

Given this JSP page, extract:
1. Page name
2. List of attributes used (input fields, selects, textareas) like policyNumber, dob, sumAssured
3. Actions performed (e.g., SubmitClaim, UpdatePolicy)
4. Relationships between fields and entities

Output JSON format:
{{
  "page_name": "...",
  "fields": ["...", "..."],
  "actions": ["...", "..."],
  "relationships": [{{"from": "...", "to": "...", "relation": "..."}}]
}}

JSP Page Content:
<jsp>
{jsp_code}
</jsp>
"""

        try:
            # Call Claude 3 Haiku via Bedrock
            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",  # ✅ Updated (clarified exact model ID)
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
            content = output['content'][0]['text']  # ✅ Updated (to match Bedrock's actual Claude structure)

            print("\n=== 🧠 Claude Raw Response ===")
            print(content[:1000])  # ✅ Updated (truncate for readability)

            try:
                print("\n=== ✅ Parsed Claude JSON ===")
                extracted = json.loads(content)
                print(json.dumps(extracted, indent=2))

                # === Optional: Save Results to S3 or DynamoDB ===
                # ✅ Uncomment and configure if persistence is needed
                # s3.put_object(
                #     Bucket="jsp-legacy-results",
                #     Key=f"outputs/{key}.json",
                #     Body=json.dumps(extracted, indent=2),
                #     ContentType="application/json"
                # )

            except Exception as e:
                print("\n⚠️ Claude JSON parsing failed")
                print(f"Error: {e}")
                print("Raw text snippet:", content[:500])
                continue

        except Exception as e:
            print(f"\n❌ Claude processing failed for {key}: {e}")
            continue
        
        #=== Push to Neo4j ===
        with neo4j_driver.session() as session:
            session.write_transaction(insert_into_neo4j, extracted)
            
    neo4j_driver.close()
    return {"statusCode": 200, "body": "Claude responses printed for all JSPs."}

def insert_into_neo4j(tx, data):
    page = data.get("page_name", "UnknownPage")
    fields = data.get("fields", [])
    actions = data.get("actions", [])
    relationships = data.get("relationships", [])

    total_nodes_created = 0
    total_rels_created = 0

    # Create Page node
    result = tx.run("MERGE (p:Page {name: $page})", page=page)
    summary = result.consume()
    total_nodes_created += summary.counters.nodes_created

    # Create Field nodes
    for field in fields:
        result = tx.run("""
            MERGE (f:Field {name: $field})
            MERGE (p:Page {name: $page})-[:HAS_FIELD]->(f)
        """, field=field, page=page)
        summary = result.consume()
        total_nodes_created += summary.counters.nodes_created
        total_rels_created += summary.counters.relationships_created

    # Create Action nodes
    for action in actions:
        result = tx.run("""
            MERGE (a:Action {name: $action})
            MERGE (p:Page {name: $page})-[:SUPPORTS_ACTION]->(a)
        """, action=action, page=page)
        summary = result.consume()
        total_nodes_created += summary.counters.nodes_created
        total_rels_created += summary.counters.relationships_created

    # Create Relationships between Entities
    for rel in relationships:
        src = rel.get("from")
        tgt = rel.get("to")
        label = rel.get("relation", "RELATED")
        if src and tgt:
            result = tx.run("""
                MERGE (a:Entity {name: $src})
                MERGE (b:Entity {name: $tgt})
                MERGE (a)-[:RELATED {type: $label}]->(b)
            """, src=src, tgt=tgt, label=label)
            summary = result.consume()
            total_nodes_created += summary.counters.nodes_created
            total_rels_created += summary.counters.relationships_created

    print(f"Inserted/merged {total_nodes_created} nodes and {total_rels_created} relationships for page '{page}'.")

