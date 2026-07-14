import whisper
from core.logger import logger

class ASRModel:
    def __init__(self, model_size="base"):
        """
        Initializes the Whisper Automatic Speech Recognition model.
        """
        logger.info(f"Loading Whisper model (size: {model_size})... This might take a moment.")
        try:
            self.model = whisper.load_model(model_size)
            logger.info("Whisper model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise e

    def transcribe(self, audio_path: str) -> str:
        """
        Takes an audio file path, runs it through Whisper, and returns the transcribed text.
        """
        logger.info(f"Transcribing audio file: {audio_path}")
        try:
            result = self.model.transcribe(audio_path)
            transcription = result["text"].strip()
            logger.debug(f"Transcription result: {transcription}")
            return transcription
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return ""
