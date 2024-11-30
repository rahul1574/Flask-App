from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import yt_dlp

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cur_dir = os.getcwd()

class DownloadRequest(BaseModel):
    link: str
    quality: str

@app.post("/download")
async def download_video(request: DownloadRequest):
    format_code = {
        "2160p": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]/best",
        "1440p": "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best[height<=1440][ext=mp4]/best",
        "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
        "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
        "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best",
        "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best",
        "240p": "bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[height<=240][ext=mp4]/best",
        "144p": "bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/best[height<=144][ext=mp4]/best"
    }

    if not request.link.startswith('http'):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    youtube_dl_options = {
        'format': format_code.get(request.quality, format_code["720p"]),
        'outtmpl': os.path.join(cur_dir, f'video-{request.link[-11:]}.%(ext)s'),
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(youtube_dl_options) as ydl:
            ydl.download([request.link])
        return JSONResponse(content={"message": "Download completed successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/formats/{video_url}")
async def get_formats(video_url: str):
    if not video_url.startswith('http'):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            available_qualities = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
            return {"formats": available_qualities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
