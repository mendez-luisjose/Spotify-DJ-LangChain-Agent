import streamlit as st

st.set_page_config(page_title="Spotify DJ 🎶", page_icon="🎵", layout="wide")

if "agent" not in st.session_state :
    st.session_state.agent = None  

if "sp" not in st.session_state :
    st.session_state.sp = None  

from langchain_core.messages import AIMessage, HumanMessage
from prompts import JJ_MESSAGE
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from audio_recorder_streamlit import audio_recorder
import time
from utils import speech_to_text
import os
from urllib.parse import urlparse, parse_qs
import spotipy

SCOPE = [
    'user-library-read',
    'user-read-playback-state',
    'user-modify-playback-state',
    'playlist-modify-public',
    'user-top-read'
]

#agent = initialize_agent(tools=music_player_tools)

if "chat_history" not in st.session_state :
    st.session_state.chat_history = [AIMessage(content=JJ_MESSAGE)]

if "speech_to_text_history" not in st.session_state :
    st.session_state.speech_to_text_history = []

def get_dj_response(user_query) :
    st_callback = StreamlitCallbackHandler(st.container())
    result = st.session_state.agent.invoke(
        {"input": user_query}, {"callbacks": [st_callback]})
    result = result["output"]
    return result

def main() :
    st.title("🎶 Spotify DJ Agent with LangChain")
    st.write("This is a Spotify DJ Agent Built with LangChain, is Powered by using the Gemini-Pro LLM. This Agent can Controls the Music, also Plays specifics Songs, Playlists, Albums or Artists. The User also con request for Songs Recommendations, based on Mood, Artists, Songs or Genre.")
    st.success("🛠️ Set the Credentials of your Spotify Account in the Sidebar")
    st.markdown("<hr/>", unsafe_allow_html=True)

    with st.sidebar:
        st.sidebar.markdown('''
            🧑🏻‍💻 Created by [Luis Jose Mendez](https://github.com/mendez-luisjose)
            ''')

        st.markdown("---------")
        st.title("🦜 Spotify DJ with LangChain")
        st.subheader("🤖 Powered by Gemini-Pro, LangChain, Groq and Spotify")
        st.markdown("---------")

        st.write(
            """
            Start Talking with the Spotify DJ LangChain Agent. \n
            """
        )

        st.info("This Agent can Controls the Music, also Plays specifics Songs, Playlists, Albums or Artists.")

        st.markdown("---------")

        _, col, _ = st.columns([1, 1, 1])
        if col.button("Restart Session", type="primary") :
            del st.session_state["sp"]
            st.rerun()

        st.warning("🛠️ Set the Credentials of your Spotify ID Account")

        spotify_id = st.text_input("Spotify ID", type="password")

        if (spotify_id != None and spotify_id != "") :
            auth_url = (
                f"https://accounts.spotify.com/authorize?response_type=token&client_id={spotify_id}"
                f"&scope={'%20'.join(SCOPE)}&redirect_uri=http://0.0.0.0:8000"
            )

            st.markdown(f'''
            ⚙️ Click [Here]({auth_url}) to Activate the Spotify Token
            ''')
            
            spotify_url = st.text_input("Spotify URL", type="password")
            
            if (spotify_url != None and spotify_url != "") :
                parsed_url = urlparse(spotify_url)
                fragment = parsed_url.fragment
                access_token = parse_qs(fragment)['access_token'][0]
                
                st.session_state.sp = spotipy.Spotify(auth=access_token)

                from ai_agents import initialize_agent
                from ai_tools import music_player_tools

                agent = initialize_agent(tools=music_player_tools)

                st.session_state.agent = agent
                
                st.success("✅ Spotify Account was Activated Successfully")
            
                st.markdown("---------")

                chat_with_voice = st.checkbox("Talk with your Voice 🎙️", value=False)
                st.warning("Speak very Clearly to the Microphone. To Record your Voice press the Microphone Icon.")

                if chat_with_voice :
                    footer_container = st.container()
                    with footer_container:
                        audio_bytes = audio_recorder(text="🔊 Activate Microphone", icon_size="2x")
                        
                        if (audio_bytes != None) and (chat_with_voice) :
                            with st.spinner("Transcribing..."):
                                webm_file_path = "./temp/temp_audio.mp3"
                                with open(webm_file_path, "wb") as f:
                                    f.write(audio_bytes)

                                transcript = speech_to_text(webm_file_path)
                                if transcript!="Error" and transcript!= None:
                                    st.session_state.speech_to_text_history.append(transcript)
                                    os.remove(webm_file_path)

                elif chat_with_voice!=True :
                    st.session_state.speech_to_text_history = []
            else :
                st.session_state.sp = None
            
    if (st.session_state.sp != None) : 
        for message in st.session_state.chat_history :
            if isinstance(message, HumanMessage) :
                with st.chat_message("user") :
                    st.markdown(message.content)
            else :
                with st.chat_message("assistant") :
                    st.markdown(message.content)

        user_query = st.chat_input("Type your message here...")
            
        if (user_query is not None and user_query != "") and (chat_with_voice!=True):
            st.session_state.chat_history.append(HumanMessage(content=user_query))
        
            with st.chat_message("user") :
                st.markdown(user_query)

            with st.chat_message("assistant") :
                ai_response = get_dj_response(user_query)
                message_placeholder = st.empty()
                full_response = ""
                # Simulate a streaming response with a slight delay
                for chunk in ai_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)

                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                
                # Display the full response
                message_placeholder.info(full_response)

            st.session_state.chat_history.append(AIMessage(content=ai_response))
        elif (chat_with_voice) and (len(st.session_state.speech_to_text_history) > 0):
            user_query = st.session_state.speech_to_text_history[-1]
            st.session_state.chat_history.append(HumanMessage(content=user_query))
        
            with st.chat_message("user") :
                st.markdown(user_query)

            with st.chat_message("assistant") :
                ai_response = get_dj_response(user_query)
                message_placeholder = st.empty()
                full_response = ""
                # Simulate a streaming response with a slight delay
                for chunk in ai_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)

                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                
                # Display the full response
                message_placeholder.info(full_response)

            st.session_state.chat_history.append(AIMessage(content=ai_response))

if __name__ == "__main__" :
    main()
