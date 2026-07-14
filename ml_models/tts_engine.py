import os
from gtts import gTTS
from core.logger import logger

class TTSEngine:
    def __init__(self, language="en"):
        """
        Initializes the Text-to-Speech engine.
        Unlike Whisper, gTTS doesn't load a massive model into RAM, 
        but we still use a class to manage state like 'language'.
        """
        self.language = language
        logger.info(f"Initialized TTS Engine (Language: {self.language})")

    def generate_audio(self, text: str, output_path: str) -> bool:
        """
        Takes text, converts it to speech using Google TTS, and saves it to a file.
        Returns True if successful, False if it fails.
        """
        if not text:
            logger.warning("No text provided for TTS. Skipping.")
            return False

        logger.info(f"Generating audio for text (length {len(text)}). Saving to {output_path}")
        try:
            # gTTS creates the audio object
            tts = gTTS(text=text, lang=self.language, slow=False)
            # We save it to the provided file path
            tts.save(output_path)
            
            logger.debug(f"Audio file successfully saved at: {output_path}")
            return True
        except Exception as e:
            logger.error(f"TTS Generation failed: {e}")
            return False
