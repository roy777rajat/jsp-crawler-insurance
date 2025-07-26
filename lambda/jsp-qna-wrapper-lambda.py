import json
import boto3

lambda_client = boto3.client('lambda')
apigw_client = boto3.client('apigatewaymanagementapi',
                          endpoint_url='https://4hnchd4nrk.execute-api.eu-west-1.amazonaws.com/production')

QNA_LAMBDA_NAME = "jsp-qna-with-llm-backed-by-redis"

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']

    # Parse the JSON string in 'body' to extract the query
    print(f"Event Coming*********   :{event}")
    try:
        body = json.loads(event.get('body', '{}'))
        query_text = body.get('query') or body.get('message')
        if not query_text:
            raise ValueError("Missing 'query' or 'message' in body")
    except Exception as e:
        send_message(connection_id, {"error": "Invalid message format or missing query."})
        return {'statusCode': 400}


    # Invoke QnA Lambda synchronously with the query
    try:
        response = lambda_client.invoke(
            FunctionName=QNA_LAMBDA_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps({"query": query_text})
        )
        qna_payload = json.loads(response['Payload'].read())
    except Exception as e:
        send_message(connection_id, {"error": f"QnA Lambda invocation failed: {str(e)}"})
        return {'statusCode': 500}

    # Send QnA Lambda response back to client
    send_message(connection_id, qna_payload)

    return {'statusCode': 200}

def send_message(connection_id, message_dict):
    try:
        apigw_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message_dict).encode('utf-8')
        )
    except apigw_client.exceptions.GoneException:
        print(f"Connection {connection_id} is gone, cannot send message.")
