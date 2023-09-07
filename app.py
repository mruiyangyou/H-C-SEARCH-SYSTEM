import streamlit as st 
import pandas as pd 
import warnings
import numpy as np
import boto3
import os
from st_files_connection import FilesConnection

# SET UP THE S3 CONNECTION AND PAGE
st.set_page_config(
    page_title='Search Database'
)

conn = st.experimental_connection('s3', type=FilesConnection)

# s3 = boto3.client('s3', aws_access_key_id='AKIA4QFGEH7S4R4P3FV7',
#                         aws_secret_access_key='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')
warnings.filterwarnings('ignore')


def search_data(input1, data):
    sheet = data.loc[data.seq == input1, 'source']
    
    if len(sheet) == 0:
       return None
    
    else:
        sheet = sheet.values[0]
        data = pd.read_excel('data/HC.xlsx', sheet_name=sheet, index_col=0)
        
        output = data.loc[data['编号'] == input1]
        output['dollar'] = (output['成品价'] * 1.2) / 7.6
        return (sheet, output)
       
def create_all_data(inputs, data):
    res = data[data['seq'].isin(inputs)]
    
    missing_choices = [choice for choice in inputs if choice not in data['seq'].values]
    
    missing_df = missing_rows = pd.DataFrame({
                'seq': missing_choices,
                '成分': [np.nan] * len(missing_choices),
                'price': [np.nan] * len(missing_choices),
            })
    
    res = pd.concat([res, missing_df])
    
    return res
    
    
st.title('H&C Search Database')

@st.cache_data 
def load_data(name):
    return pd.read_csv(f'data/{name}.csv')

df2 = load_data('source')
df3 = load_data('price')


with st.container():
    number = st.text_input("Ente the number of textile you want to search", placeholder='1, 2, 3...')
   
st.divider()

inputs = []
button = False
if number:
    with st.container():
        for idx in range(int(number)):
            unique_label = f'Enter the sequence number #{idx+1}'  # making label unique
            # input1 = st.text_input(unique_label, placeholder='HX...')
            input1 = st.selectbox(unique_label, df2.seq.to_list())
            inputs.append(input1) 
        save = st.checkbox('Whether to save the info to cloud')
        
        if save:
            email = st.text_input('Clients Email', placeholder='...@xxx.com')
            req = st.text_input('Clients Requirments', placeholder='...')
        button = st.button('Search!')
        
        

if inputs and button:
    st.divider()
    st.header('Results:')
    for i in inputs:
        output = search_data(i, df2)
        if not output:
            st.subheader(i)
            st.write('Please retry with correct sequence number!')
        else:
            st.subheader(i + ': ' + output[0])
            st.dataframe(output[1])
        
    
if button and save and email and req:
        st.divider()
        st.subheader('Save Progress:')
        res = create_all_data(inputs, df3)
        data_path = 's3://hc-suzhou/9495LondonTextile'
        specific_path = os.path.join(data_path, email)
        emial_content = pd.DataFrame({'email': [email], 'requirements': [req]})
        if int(number) != 0:
            res.to_csv(os.path.join(specific_path, 'textile.csv'))
        emial_content.to_csv(os.path.join(specific_path, 'contacts.csv'))
        st.write("Save the above successfult to AWS S3!")