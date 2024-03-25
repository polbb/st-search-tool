import streamlit as st
import boto3
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import re

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
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_default_region)

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

    st.write(f'Number of Non-Micro companies: {len(company_ids)}')

    # Initialize empty list to store s3Keys
    s3_keys = []

    # Add a progress bar to visualize s3Key extraction progress
    progress_bar = st.progress(0)
    total_companies = len(company_ids)

    # Initialize list to store sentences matching the fuzzy search
    matching_sentences = []

    # Collect s3Keys from company_xhtml table using collected companyIDs
    for index, company_id in enumerate(company_ids):
        st.write(f'Processing company: {company_id}')
        response = xhtml_table.get_item(
            Key={'companyID': company_id}
        )
        if 'Item' in response:
            s3_key = response['Item']['object_key']
            s3_keys.append(s3_key)
            
            # Retrieve the xhtml file content from S3
            s3_object = s3.get_object(Bucket='company-house', Key=s3_key)
            s3_content = s3_object['Body'].read().decode('utf-8')
            
            # Use BeautifulSoup to extract all text from the xhtml file
            soup = BeautifulSoup(s3_content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            
            # Split the text into sentences
            sentences = re.split(r'(?<=[.!?]) +', text)
            
            # Perform fuzzy search on each sentence
            for sentence in sentences:
                if fuzz.partial_ratio(fuzzy_search.lower(), sentence.lower()) > 80:
                    sentence_index = sentences.index(sentence)
                    context = ' '.join(sentences[max(0, sentence_index-1):min(len(sentences), sentence_index+2)])
                    matching_sentences.append(context)
                    break  # Assuming we only need the first match per company
        
        # Update progress bar
        progress_bar.progress((index + 1) / total_companies)

    st.write('Matching Sentences:', matching_sentences)

