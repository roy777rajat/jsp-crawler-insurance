import boto3
import streamlit as st


def list_jsp_files_s3(bucket_name):
    s3 = get_s3_client()
    response = s3.list_objects_v2(Bucket=bucket_name)
    return [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].endswith(".jsp")]

def get_jsp_html(bucket_name, key):
    s3 = get_s3_client()
    response = s3.get_object(Bucket=bucket_name, Key=key)
    return response["Body"].read().decode("utf-8")

def check_aws_connection():
    try:
        s3 = get_s3_client()
        s3.list_buckets()
        print("✅ AWS connection successful.")
        return True
    except Exception as e:
        print(f"❌ AWS connection failed: {e}")
        return False
    
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
        aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"],
        region_name=st.secrets["aws"]["region"]
    )