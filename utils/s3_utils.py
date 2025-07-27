import boto3
import streamlit as st
import os

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
        aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"],
        region_name=st.secrets["aws"]["region_name"]
    )
    # return boto3.client("s3")

def list_jsp_files_s3(bucket_name):
    try:
        s3 = get_s3_client()
        response = s3.list_objects_v2(Bucket=bucket_name)
        return [
            obj["Key"]
            for obj in response.get("Contents", [])
            if obj["Key"].endswith(".jsp")
        ]
    except Exception as e:
        st.error(f"Failed to list JSP files in S3: {e}")
        return []

def get_jsp_html(bucket_name, key):
    try:
        s3 = get_s3_client()
        response = s3.get_object(Bucket=bucket_name, Key=key)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        st.error(f"Failed to fetch JSP content: {e}")
        return ""

def check_aws_connection():
    try:
        s3 = get_s3_client()
        s3.list_buckets()
        print("✅ AWS connection successful.")
        return True
    except Exception as e:
        print(f"❌ AWS connection failed: {e}")
        return False

def get_websocket_url_local():
    return os.getenv("WEBSOCKET_URL", "ws://localhost:8000")
def get_websocket_url_server():
    return st.secrets["aws"]["websocket_url"]
    