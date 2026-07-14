# 1. pydantic_settings: This is a library extending Pydantic specifically for settings/configuration management.
# 2. BaseSettings: A class from pydantic-settings. Subclasses automatically load values from environment variables or .env files.
# 3. SettingsConfigDict: A configuration helper type to customize how BaseSettings discovers, parses, and encodes configuration sources.
from pydantic_settings import BaseSettings, SettingsConfigDict

# 4. class Settings(BaseSettings): Defines our custom configuration schema by inheriting from BaseSettings.
class Settings(BaseSettings):
    # API Settings
    # 5. PROJECT_NAME: str = "Voicebot API": Defines a string variable representing the title of our API. Defaults to "Voicebot API".
    PROJECT_NAME: str = "Voicebot API"
    # 6. API_V1_STR: str = "/api/v1": Defines the base path string for version 1 of our API endpoints.
    API_V1_STR: str = "/api/v1"
    
    # Model Configurations
    # 7. WHISPER_MODEL_SIZE: str = "base": Declares which OpenAI Whisper speech-to-text model size to download and use ('base' is fast & accurate).
    WHISPER_MODEL_SIZE: str = "base"
    # 8. BERT_MODEL_PATH: str = "bert-base-uncased": The Hugging Face hub path for our intent-classification BERT model (case-insensitive).
    BERT_MODEL_PATH: str = "bert-base-uncased" # Or your custom path
    
    # Environment config loading
    # 9. model_config: A special attribute Pydantic reads to set settings behavior.
    # 10. SettingsConfigDict(...): Customizes loading behavior.
    # - env_file=".env": Tells the system to search for a file named '.env' in the root directory.
    # - env_file_encoding="utf-8": Uses the standard UTF-8 text encoding format to read the .env file.
    # - extra='ignore': Ensures that extra variables in the environment that are not declared in this class are safely ignored.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')

# 11. settings = Settings(): Instantiates the class once to load all variables.
# Importing this object elsewhere imports a pre-loaded configuration singleton.
settings = Settings()