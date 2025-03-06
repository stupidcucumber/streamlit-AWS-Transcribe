import streamlit as st
import boto3
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from src.transcribe import transcribe


st.set_page_config(
    page_title="Transcribe Video",
    page_icon="📝",
)
st.title('📝 Transcribe Video')
st.caption('Upload your video to add subtitles to it!')


if st.session_state.get("AWS_TRANSCRIBE_CLIENT") is None:
    load_dotenv()
    
    if os.getenv("AWS_ACCESS_KEY_ID") is None or os.getenv("AWS_SECRET_ACCESS_KEY") is None:
        st.error("⚠️ Problem with the AWS Credentials Keys!")

    else:
        st.session_state["AWS_TRANSCRIBE_CLIENT"] = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        ).client(service_name="transcribe", region_name="eu-north-1")


if st.session_state.get("AWS_S3_CLIENT") is None:
    load_dotenv()
    
    if os.getenv("AWS_ACCESS_KEY_ID") is None or os.getenv("AWS_SECRET_ACCESS_KEY") is None:
        st.error("⚠️ Problem with the AWS Credentials Keys!")
        
    else:
        st.session_state["AWS_S3_CLIENT"] = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        ).client(service_name="s3", region_name="eu-north-1")
    


left_column, right_column = st.columns(2)


with left_column:
    
    st.file_uploader("Upload video", key="input_video", type=[".mp4", ".avi", ".mov"])


with right_column:
    
    if st.session_state.input_video:
        video_name = st.session_state.input_video.name
        video_path = Path(f"{datetime.now().strftime("%d-%m-%YT%H-%M-%S")}_{video_name}")
        
        if not video_path.exists():
            video_path.write_bytes(st.session_state.input_video.read())
        
        subtitles = transcribe(
            video_path=video_path, 
            transcribe_client=st.session_state.get("AWS_TRANSCRIBE_CLIENT"), 
            s3_client=st.session_state.get("AWS_S3_CLIENT"), 
            bucket=os.getenv("AWS_BUCKET_NAME")
        )
        
        video_path.unlink()
        
        st.video(st.session_state.input_video, subtitles=subtitles)
