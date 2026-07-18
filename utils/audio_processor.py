import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url :str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

    # Try different extraction strategies to bypass bot detection/rate limits
    configs_to_try = [
        # 1. Impersonate Android/iOS mobile apps (highly successful, no browser access needed)
        {
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios"]
                }
            }
        },
        # 2. Try default (no cookies, no spoofing)
        {},
        # 3. Fallback to extracting cookies from Chrome
        {
            "cookiesfrombrowser": ("chrome",)
        },
        # 4. Fallback to Safari
        {
            "cookiesfrombrowser": ("safari",)
        },
        # 5. Fallback to Firefox
        {
            "cookiesfrombrowser": ("firefox",)
        }
    ]

    base_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    last_error = None
    for config in configs_to_try:
        ydl_opts = base_opts.copy()
        ydl_opts.update(config)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".wav"
                return filename
        except Exception as e:
            last_error = e
            continue

    if last_error:
        raise last_error
    raise RuntimeError("Failed to download audio.")




data = download_youtube_audio("https://www.youtube.com/watch?v=7HSSR1n8dgc")


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz for monoaudio
    audio.export(output_path, format="wav")
    return output_path
    
data_final = convert_to_wav(data)

#convert big audio in chunks

def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

print(chunk_audio(data_final))



