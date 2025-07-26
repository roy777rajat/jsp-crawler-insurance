import json
import boto3

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    
    print(f"Client connected: {connection_id}")
    
    return {
        "statusCode": 200,
        "body": "Connected successfully."
    }
