import streamlit as st
import boto3



# Streamlit UI
st.set_page_config(layout="wide")  # Force wide mode
with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

# AWS Credentials
aws_access_key_id = st.secrets.AWS_ACCESS_KEY_ID
aws_secret_access_key = st.secrets.AWS_SECRET_ACCESS_KEY
aws_default_region = st.secrets.AWS_DEFAULT_REGION

# AWS Services Clients
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_default_region)
dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_default_region)



st.title("ArgoXai")
col1, col2, _, _, _, _, _, _ = st.columns([3,3,1,1,1,1,1,1])
company_number = col1.text_input("Enter CIK code")
data = st.button("Retrieve Data")

if data:
    # Ensure the CIK is a string and has leading zeros if necessary
    cik_str = company_number.zfill(10)
    
    # Retrieve s3 key from DynamoDB for Risk Factors
    table = dynamodb.Table('sec_text')
    response = table.get_item(Key={'companyID': cik_str})


