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
    # Display the collected companyIDs
    ratios_table = dynamodb.Table('company_ratios')
    xhtml_table = dynamodb.Table('company_xhtml')

    # Initialize empty list to store companyIDs where non_micro == True
    company_ids = []

    # Initialize the scan for company_ratios table
    response = ratios_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('non_micro').eq(True)
    )

    # Collect companyIDs
    company_ids.extend(item['companyID'] for item in response['Items'])

    # Handle pagination if there's more data to scan in company_ratios table
    while 'LastEvaluatedKey' in response:
        response = ratios_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('non_micro').eq(True),
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        company_ids.extend(item['companyID'] for item in response['Items'])

    # Initialize empty list to store s3Keys
    s3_keys = []

    # Collect s3Keys from company_xhtml table using collected companyIDs
    for company_id in company_ids:
        response = xhtml_table.get_item(
            Key={'companyID': company_id}
        )
        if 'Item' in response:
            s3_keys.append(response['Item']['s3Key'])

    st.write(s3_keys)


