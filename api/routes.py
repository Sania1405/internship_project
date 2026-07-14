# 1. APIRouter: Helps modularize routes into separate files instead of cluttering main.py.
# 2. File, UploadFile: FastAPI form-data classes to handle binary uploads (like wav/mp3 audio files) from HTML pages.
from fastapi import APIRouter, File, UploadFile
# 3. shutil: Standard library utility to perform file operations (copying bytes from raw upload to disk).
import shutil
# 4. os: Standard module to interact with host file system (checking if file exists, deleting temp files).
import os

from core.logger import logger
# 5. ml_registry: Imports the global registry containing pre-loaded models from main.py.
from api.main import ml_registry

# 6. router = APIRouter(): Creates the router instance to register our routes.
router = APIRouter()

# 7. @router.post("/chat"): Defines a POST endpoint at "/chat" to receive multi-part form data containing audio.
@router.post("/chat")
async def chat_with_bot(audio_file: UploadFile = File(...)):
    """
    The main endpoint for the Voicebot. 
    1. Receives audio from Grandma's phone.
    2. Uses ASR (Whisper) to get text.
    3. Uses BERT to get intent.
    4. Uses TTS to generate an audio response.
    """
    logger.info(f"Received new voice request: {audio_file.filename}")

    # 8. temp_audio_path: Generates a temporary filename, e.g., 'temp_live_voice.wav'.
    temp_audio_path = f"temp_{audio_file.filename}"
    # 9. open(temp_audio_path, "wb"): Creates a physical empty file in 'write binary' mode on the server disk.
    with open(temp_audio_path, "wb") as buffer:
        # 10. copyfileobj: Copies raw uploaded binary chunks from memory/temp cache directly into the open file.
        shutil.copyfileobj(audio_file.file, buffer)

    try:
        # 11. user_text: Passes the path of the saved wav file to Whisper for locally-run transcription.
        user_text = ml_registry['asr'].transcribe(temp_audio_path)
        # 12. If Whisper returns nothing (silence or error), returns a JSON error response.
        if not user_text:
            return {"error": "Could not understand audio."}

        # 13. bot_reply: Sends the transcribed string to the Llama-3.1 agent. It decides on tools and returns a reply string.
        bot_reply = ml_registry['agent'].chat(user_text)
        
        # 14. response_audio_path: Defines output filename for synthesized speech, e.g., 'response_live_voice.wav.mp3'.
        response_audio_path = f"response_{audio_file.filename}.mp3"
        # 15. generate_audio: Sends the reply string to gTTS, which contacts Google and saves the voice response locally as MP3.
        tts_success = ml_registry['tts'].generate_audio(bot_reply, response_audio_path)

        # 16. Returns success payload including transcription, text response, and audio success flag.
        return {
            "success": True,
            "user_said": user_text,
            "bot_reply": bot_reply,
            "audio_file_ready": tts_success
        }
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        # 17. In case of unhandled error (OOM, PyTorch crash), returns a standard HTTP error.
        return {"error": "Internal Server Error"}
        
    finally:
        # 18. finally block: Runs ALWAYS, even if transcription failed or the server crashed.
        # It removes the temporary uploaded audio file from disk so the server's hard drive does not run out of space.
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
