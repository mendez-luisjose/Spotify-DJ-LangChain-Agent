import requests
import os
import string
import streamlit as st
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

DEEPGRAM_API_KEY = st.secrets["DEEPGRAM_API_KEY"]

DEEPGRAM_URL = "https://api.deepgram.com/v1/speak?model=aura-luna-en"

def text_to_speech(text) :
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    
    text = text.translate(str.maketrans('', '', string.punctuation))
    text_lower = text.lower()

    payload = {
        "text": text_lower
    }

    audio_file_path = "./temp/temp_audio_play.mp3"  # Path to save the audio file

    with open(audio_file_path, 'wb') as file_stream:
        response = requests.post(DEEPGRAM_URL, headers=headers, json=payload, stream=True)
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file_stream.write(chunk) # Write each chunk of audio data to the file

    return audio_file_path

def speech_to_text(speech_file_path) :
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        with open(speech_file_path, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        # STEP 4: Print the response
        return response["results"]["channels"][0]["alternatives"][0]["transcript"]

    except Exception as e:
        return "Error"
    
    
