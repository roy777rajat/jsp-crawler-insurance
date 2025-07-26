import json
import boto3

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    body = event.get('body', '')
    
    print(f"Default handler: received from {connection_id} → {body}")
    
    # Echo back the message as fallback
    apigw_management = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url = f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
    )
    
    try:
        apigw_management.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps({"error": "Unknown route", "echo": body})
        )
    except Exception as e:
        print(f"Error sending default response: {str(e)}")

    return {
        "statusCode": 200,
        "body": "Default route triggered"
    }
