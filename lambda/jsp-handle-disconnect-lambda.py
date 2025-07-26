import json
import boto3

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    
    # Optionally remove from DynamoDB or log
    print(f"Client disconnected: {connection_id}")
    
    return {
        "statusCode": 200,
        "body": "Disconnected successfully."
    }
