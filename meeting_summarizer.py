import streamlit as st
import requests
import pandas as pd
from get_results import *

if 'start_point' not in st.session_state:
    st.session_state['start_point'] = 0

def update_start(start_t):
    st.session_state['start_point'] = int(start_t/1000)

uploaded_file = st.file_uploader('Please upload a file')

if uploaded_file is not None:
    st.audio(uploaded_file, start_time=st.session_state['start_point'])
    polling_endpoint = upload_to_AssemblyAI(uploaded_file)
    
    status='submitted'
    while status != 'completed':
        polling_response = requests.get(polling_endpoint, headers=headers)
        print(polling_response.json())
        status = polling_response.json()['status']

        if status == 'completed':
            # display utterances for each speaker
            st.subheader('Summary notes of this meeting')
            utterances = polling_response.json()['utterances']
            utterances_df = pd.DataFrame(utterances)
            utterances_df['start_str'] = utterances_df['start'].apply(convertMillis)
            utterances_df['end_str'] = utterances_df['end'].apply(convertMillis)

            for index, row in utterances_df.iterrows():
                st.write(f"Speaker {row['speaker']}: {row['text']}")
                st.button(row['start_str'], on_click=update_start, args=(row['start'],), key=index)
