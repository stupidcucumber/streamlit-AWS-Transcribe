from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess
import boto3
from urllib.parse import urlparse
from src.logging import getLogger
from datetime import datetime


logger = getLogger(__name__)


def get_audio(
    video_path: Path,
    audio_path: Path
) -> None:
    logger.info(f"Extracting audio to {audio_path}.")
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            video_path.as_posix(),
            "-q:a",
            "0",
            "-map",
            "a",
            audio_path.as_posix(),
            "-y"
        ]
    )
    
    
def transcribe(
    video_path: Path,
    transcribe_client: boto3.Session,
    s3_client: boto3.Session,
    bucket: str
) -> Path:
    logger.info(f"Start transcribing video {video_path}")
    
    with NamedTemporaryFile(suffix=".mp3", prefix=datetime.now().strftime("%d-%m-%YT%H-%M-%S_")) as tmp:
        get_audio(video_path=video_path, audio_path=Path(tmp.name))
        
        logger.info("Uploading file to the S3 Bucket")
        s3_client.upload_file(Path(tmp.name), bucket, f"{video_path.stem}.mp3")
        
    logger.info("Starting transcription job.")
    response = transcribe_client.start_transcription_job(
        TranscriptionJobName=video_path.stem,
        IdentifyLanguage=True,
        MediaFormat="mp3",
        Media={
            "MediaFileUri": f"s3://{bucket}/{video_path.stem}.mp3",
        },
        OutputBucketName=bucket,
        OutputKey=f"{video_path.stem}",
        Subtitles={
            "Formats": ["srt"],
            "OutputStartIndex": 1
        }
    )

    while True:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=video_path.stem
        )
        
        if response["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
            subtitles_uri = urlparse(response["TranscriptionJob"]["Subtitles"]["SubtitleFileUris"][0])
            
            logger.info("Downloading subtitles.")
            s3_client.download_file(bucket, subtitles_uri.path.split("/")[-1], f"{video_path.stem}.srt")
            
            break
        
    logger.info("Transcription finished.")
    return Path(f"{video_path.stem}.srt")
        
        