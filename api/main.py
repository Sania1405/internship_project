# 1. FastAPI: The core framework used to build our high-performance asynchronous web APIs.
from fastapi import FastAPI
# 2. CORSMiddleware: Browser security utility allowing foreign frontends (like a local HTML webpage) to request our API.
from fastapi.middleware.cors import CORSMiddleware
# 3. StaticFiles: Utility to serve static assets (like raw generated MP3 audio files) over HTTP urls.
from fastapi.staticfiles import StaticFiles
# 4. asynccontextmanager: Python standard helper to define server startup/shutdown hooks (lifespan events).
from contextlib import asynccontextmanager
# 5. logger: Our custom structured logger to print server statuses.
from core.logger import logger
# 6. load_dotenv: Reads the local '.env' text file and injects all keys/passwords into system variables.
from dotenv import load_dotenv

# 7. load_dotenv(): Executed immediately to ensure API keys are injected before models attempt to load.
load_dotenv()

# 8. Importing our custom wrappers for Whisper ASR, Google TTS, ChromaDB RAG, and Groq LLM Agent.
from ml_models.asr_whisper import ASRModel
from ml_models.tts_engine import TTSEngine
from ml_models.rag_system import RAGSystem
from ml_models.agent_llm import AgentLLM

# 9. ml_registry: Global dictionary in RAM that stores model objects so they persist across requests.
ml_registry = {}

# 10. lifespan(app): A wrapper containing hooks that run before the server accepts requests and after it stops.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function handles the startup and shutdown of the server.
    """
    logger.info("Server is starting up... Hiring our AI Employees!")
    
    try:
        # 11. Load local heavy AI models (ASR and TTS)
        # - ASRModel() downloads/loads Whisper base weights into RAM/VRAM.
        # - TTSEngine(language="en") sets up the Google voice language wrapper.
        ml_registry['asr'] = ASRModel()
        ml_registry['tts'] = TTSEngine(language="en")
        
        # 12. RAGSystem(): Reads data/job_description.txt, indexes it to ChromaDB in RAM.
        ml_registry['rag'] = RAGSystem()
        
        # 13. AgentLLM(...): Instantiates the Groq model, linking the RAG system as a tool dependency.
        ml_registry['agent'] = AgentLLM(ml_registry['rag'])
        
        logger.info("All ML systems (ASR, TTS, RAG, Agent) are loaded and ready!")
    except Exception as e:
        logger.error(f"Critical failure during model loading: {e}")
        # 14. If models fail to load, raising the error crashes Uvicorn to prevent running in a broken state.
        raise e

    # 15. yield: Pauses execution here. Server is now fully up and accepting API calls to /chat.
    yield 

    # 16. Shut Down Hook: Runs when you stop the server (e.g. pressing Ctrl+C).
    logger.info("Server is shutting down... Clearing ML registry.")
    # 17. ml_registry.clear(): Empties dictionary references to free up system RAM.
    ml_registry.clear()

# 18. voicebot_router: Importing endpoints. Imported here to prevent circular imports with main.py.
from api.routes import router as voicebot_router

# 19. app = FastAPI(...): Creates the global FastAPI application instance, linking the lifespan hooks.
app = FastAPI(title="AI Voicebot API", lifespan=lifespan)

# 20. CORS Settings: Configures access headers allowing our browser file to upload audio.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any local origin/port to send API requests.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.).
    allow_headers=["*"],  # Allows all headers.
)

# 21. app.mount(...): Maps local folder "." (project root) to url path "/audio". 
# Allows frontend to retrieve generated MP3 files via http://127.0.0.1:8000/audio/filename.mp3.
app.mount("/audio", StaticFiles(directory="."), name="audio")

# 22. app.include_router(...): Connects all routes defined in routes.py to this app instance.
app.include_router(voicebot_router)

# 23. @app.get("/health"): A fast GET endpoint for status checks.
@app.get("/health")
def health_check():
    """A simple endpoint to prove the server is running and models are loaded."""
    logger.info("Health check endpoint pinged.")
    return {"status": "Online", "models_ready": len(ml_registry) == 3}
