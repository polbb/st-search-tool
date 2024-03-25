import streamlit as st
import boto3

# Streamlit UI
st.set_page_config(layout="wide")  # Force wide mode
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# AWS Credentials
aws_access_key_id = st.secrets.AWS_ACCESS_KEY_ID
aws_secret_access_key = st.secrets.AWS_SECRET_ACCESS_KEY
aws_default_region = st.secrets.AWS_DEFAULT_REGION

# AWS Services Clients
dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_default_region)

st.title("ArgoXai")
col1, col2, _, _, _, _, _, _ = st.columns([3,3,1,1,1,1,1,1])
fuzzy_search = col1.text_input("Search Documents")
data = st.button("Search")
st.divider()

if data:
    # st.write("inside if data")
    # Display the collected companyIDs
    table = dynamodb.Table('company_ratios')
    # st.write("after db table")

    # Initialize empty list to store companyIDs where non_micro == True
    company_ids = []
    # st.write(company_ids)

    # Initialize the scan
    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('non_micro').eq(True)
    )

    # Collect companyIDs
    company_ids.extend(item['companyID'] for item in response['Items'])

    # Handle pagination if there's more data to scan
    while True:
        if 'LastEvaluatedKey' not in response:
            break
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('non_micro').eq(True),
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        company_ids.extend(item['companyID'] for item in response['Items'])

    st.write("Companies with non_micro == True:", company_ids)

