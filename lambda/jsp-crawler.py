# Created by Rajat on 2024-03-08
# Tihs code is part of a project to analyze JSP files using AWS Bedrock and store the results in a Neo4j graph database.
# One time or incremental run to extract data from JSP files in an S3 bucket and store it in Neo4j.

import json 
import boto3
import time
from neo4j import GraphDatabase # Rajat : You have to install the neo4Jdriver


secretsmanager = boto3.client("secretsmanager", region_name="eu-west-1")
def get_secrets(secret_name):
    try:
        response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response['SecretString'])
        return secret_dict
    except Exception as e:
        print(f" Failed to retrieve {secret_name} credentials: {e}")
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
    print("=== Rajat....Lambda triggered! ===")
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=JSP_PREFIX)
    if "Contents" not in response:
        return {"statusCode": 404, "body": "No JSPs found in the bucket."}
    
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("All data wiped out Neo4j graph cleared.")  # It has to be one time OR if you need to clear and fresh insrt can kepp

    for obj in response["Contents"]:
        key = obj["Key"]
        if not key.endswith(".jsp"):
            continue

        print(f"\n=== Processing JSP: {key} ===")
        jsp_code = s3.get_object(Bucket=BUCKET_NAME, Key=key)['Body'].read().decode("utf-8")

        prompt = f"""
You are a Legacy JSP Page Analyst for an Insurance company. Output ONLY the JSON in exact format. Do NOT add explanations or any other text.

Given this JSP page, extract:
1. Page name
2. JSP file name (exact full filename like PolicyCancellation.jsp)
3. List of attributes used (input fields, selects, textareas) like policyNumber, dob, sumAssured
4. Actions performed (e.g., SubmitClaim, UpdatePolicy)
5. Relationships between fields and entities

Output JSON format:
{{
  "page_name": "...",
  "jsp_name": "...",
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
            response = call_bedrock_with_retry(bedrock, prompt)
            raw_output = response['body'].read()
            output = json.loads(raw_output)
            content = output['content'][0]['text']

            print("\n=== 🧠 Claude Raw Response ===")
            print(content[:1000])

            try:
                print("\n=== Rajat Sucessfully....Parsed Claude JSON ===")
                extracted = json.loads(content)
                print(json.dumps(extracted, indent=2))

                
                print(f"DEBUG Extracted | page_name: {extracted.get('page_name')}, jsp_name: {extracted.get('jsp_name')}, fields: {extracted.get('fields')}, actions: {extracted.get('actions')}")

            except Exception as e:
                print("\nClaude JSON parsing failed")
                print(f"Error: {e}")
                print("Raw text snippet:", content[:500])
                continue

        except Exception as e:
            print(f"\n Claude processing failed for {key}: {e}")
            continue
        
        with neo4j_driver.session() as session:
            session.write_transaction(insert_into_neo4j, extracted)
            
    neo4j_driver.close()
    return {"statusCode": 200, "body": "Claude responses printed for all JSPs."}


def insert_into_neo4j(tx, data):
    page = data.get("page_name", "UnknownPage")
    jsp_name = data.get("jsp_name", "Unknown.jsp")
    fields = data.get("fields", [])
    actions = data.get("actions", [])
    relationships = data.get("relationships", [])

    total_nodes_created = 0
    total_rels_created = 0

    # Create and return the Page node to reuse it
    result = tx.run("""
        MERGE (p:Page {name: $page})
        SET p.jsp_name = $jsp_name
        RETURN p
    """, page=page, jsp_name=jsp_name)
    page_node = result.single()["p"]

    for field in fields:
        result = tx.run("""
            MERGE (f:Field {name: $field})
            WITH f
            MATCH (p:Page {name: $page})
            MERGE (p)-[:HAS_FIELD]->(f)
        """, field=field, page=page)
        summary = result.consume()
        total_nodes_created += summary.counters.nodes_created
        total_rels_created += summary.counters.relationships_created

    for action in actions:
        result = tx.run("""
            MERGE (a:Action {name: $action})
            WITH a
            MATCH (p:Page {name: $page})
            MERGE (p)-[:SUPPORTS_ACTION]->(a)
        """, action=action, page=page)
        summary = result.consume()
        total_nodes_created += summary.counters.nodes_created
        total_rels_created += summary.counters.relationships_created

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



def call_bedrock_with_retry(bedrock, prompt, max_retries=5):
    for attempt in range(max_retries):
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
            return response
        except bedrock.exceptions.ThrottlingException as e:
            wait_time = (2 ** attempt)
            print(f"Throttled, retrying after {wait_time}s... (attempt {attempt + 1})")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            raise
    raise Exception("Max retries exceeded due to throttling.")
