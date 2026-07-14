# AI Voicebot Mock Interview Preparation Log

This document tracks the questions and ideal model answers for the AI Voicebot project.

---

## 📂 Module 1: Core Configuration & Logger (`core/`)

### Question 1: BaseSettings and Environment Variables
**Question**: In your `config.py` file, you inherit from `BaseSettings` to manage configuration variables. Why is this approach preferred in a production environment over simply hardcoding configuration values directly into the code? How does `BaseSettings` load environment variables dynamically when your app is deployed?

**Ideal Answer**:
In production, we separate configuration from code to adhere to clean-code principles (such as the Twelve-Factor App methodology) and to keep secrets like API keys secure. Hardcoding makes the application fragile, couples the code to a single environment, and risks leaking credentials.

By inheriting from Pydantic's `BaseSettings` in `config.py`, we get two main benefits:
1. **Dynamic Loading**: It automatically looks up system environment variables first, and then falls back to loading variables from a `.env` file (configured via `SettingsConfigDict`).
2. **Type Safety and Validation**: Unlike standard `os.getenv` which reads everything as a string, `BaseSettings` automatically parses and validates types. If a port should be an integer, Pydantic guarantees it is converted and validated on startup. If key variables are missing or incorrectly typed, the application crashes immediately with a clear validation error, preventing silent runtime failures in production.

---

### Question 2: Logger Level Hierarchy Debugging
**Question**: Let's assume you deploy the app, and you want to debug Whisper's behavior. In the code, we call `logger.debug(f"Transcription result: {transcription}")`. However, when candidates answer questions, you notice that *nothing* is being written to the `logs/app.log` file, even though `file_handler.setLevel(logging.DEBUG)` is configured. 

1. What is the root cause of this bug?
2. What exact line of code in `logger.py` would you modify to fix it?

**Ideal Answer**:
1. **Root Cause**: Python's logging system uses a two-stage filtering hierarchy. First, messages are filtered at the global **Logger** level, and then they are filtered at the individual **Handler** level. Currently, the main logger is set to `INFO` (`logger.setLevel(logging.INFO)`). Therefore, any `DEBUG` messages are blocked at Stage 1 and never reach the `file_handler` in Stage 2, despite `file_handler` being set to `DEBUG`.
2. **Correction**: Modify the main logger level to `DEBUG` on line 16 of `logger.py`:
   ```python
   logger.setLevel(logging.DEBUG)
   ```
   This allows `DEBUG` messages to pass Stage 1. Then, the handlers will filter them individually: `console_handler` will show only `INFO` in the terminal, while `file_handler` will write both `INFO` and `DEBUG` messages to the `app.log` file on disk.

---

## 📂 Module 2: FastAPI Backbone & API Server (`api/main.py`)

### Question 3: FastAPI Lifespan and Model Caching
**Question**: What is the purpose of FastAPI's `lifespan` event manager, and why do you load your machine learning models inside it?

**Ideal Answer**:
ML models (like OpenAI Whisper) have large weight parameters. Loading them from disk into CPU/GPU RAM takes substantial time (5–15 seconds). If we loaded them inside the HTTP route handlers on every request, every API call would suffer from huge delays, making the voicebot unusable. 

By using FastAPI's `lifespan` manager, we can load the models once at server startup, cache them in a global memory registry (`ml_registry`), and keep them resident in RAM. When incoming user requests arrive, inference executes instantly. Furthermore, `lifespan` allows us to run clean-up tasks (like `ml_registry.clear()`) when the server shuts down, freeing up the machine's memory safely.

---

### Question 4: CORS Middleware
**Question**: What is CORS, and why did you configure `CORSMiddleware` with `allow_origins=["*"]`?

**Ideal Answer**:
CORS stands for **Cross-Origin Resource Sharing**. It is a browser security mechanism that blocks a frontend application hosted on one origin (e.g., `localhost:5500`) from making HTTP requests (like audio uploads) to a backend API running on a different origin (e.g., `localhost:8000`).

To allow our glassmorphic HTML/JS frontend to talk to our FastAPI backend, we configured `CORSMiddleware` with `allow_origins=["*"]`. This header tells the candidate's browser that the API is publicly open to requests from any domain, preventing the browser from blocking the voicebot upload requests.

---

### Question 5: Exposing Static Files
**Question**: Why did you mount static files using `app.mount("/audio", StaticFiles(directory="."), name="audio")`?

**Ideal Answer**:
Our Text-to-Speech (TTS) engine generates voice responses and saves them as physical MP3 files locally on the server's hard disk. To let the candidate's browser play these audio responses, the files must be accessible over the internet via HTTP.

Mounting the directory using `StaticFiles(directory=".")` maps the local filesystem directory to the URL path `/audio`. This allows the frontend HTML `<audio>` element to fetch and play the generated file directly from `http://127.0.0.1:8000/audio/response_live_voice.wav.mp3`.

---

### Question 6: HTTP POST vs. GET for Binary Uploads
**Question**: The `/chat` endpoint is configured as an HTTP `POST` route. Why is a `POST` request preferred over a `GET` request for uploading voice audio files, and what are the functional differences?

**Ideal Answer**:
1. **HTTP GET**: Primarily designed for retrieving data. It transmits parameters in the URL query string (e.g. `/chat?user=123`). URLs have a length limit (around 2,048 characters in most browsers), meaning you cannot transmit binary audio files (which are megabytes of data) via GET query parameters.
2. **HTTP POST**: Designed for sending data payloads. It sends binary data inside the **HTTP Request Body** (using `multipart/form-data` encoding). It has no theoretical size limits, making it the appropriate method to transmit media/file uploads.
3. **State Change**: By REST conventions, GET requests should be idempotent (causing no server state changes/no side effects). POST requests represent state changes (e.g., uploading files, modifying databases, or executing model inference).

---

### Question 7: Temporary File Cleanup and the `finally` block
**Question**: In `routes.py`, when a file is uploaded, we save it as a temporary file on the server's disk, and then delete it inside a `finally` block. 
1. Why is it necessary to delete this file after processing?
2. Why is the deletion placed inside the `finally` block rather than at the end of the `try` block?

**Ideal Answer**:
1. **Necessity of Deletion**: If the server does not delete the uploaded voice files, the server's local storage disk will accumulate duplicate files over time. If 1,000 candidates take interviews uploading 10MB of audio each, the server will quickly run out of disk space, leading to server-wide crashes.
2. **Role of the `finally` block**: A `finally` block is guaranteed by Python to execute **no matter what happens** in the preceding code blocks. If the code inside the `try` block crashes (e.g., Whisper throws an error, or the server runs out of RAM), an early `return` or exception is triggered. 
   If the deletion was simply placed at the end of the `try` block, a crash would bypass the deletion line, leaving the temporary file on disk. Placing it in `finally` guarantees that cleanup always runs, preventing memory/storage leaks during failures.

---

### Question 8: HTTP Methods (GET, POST, PUT, DELETE)
**Question**: What are the main differences between HTTP GET, POST, PUT, and DELETE methods, and how are they mapped in REST APIs?

**Ideal Answer**:
*   **GET**: Used strictly to retrieve/fetch data from the server. It must not alter the server's state (it should be read-only/idempotent). In our project, `/health` is a GET request.
*   **POST**: Used to send data payloads to create new resources or trigger complex server-side computations (e.g., uploading candidate audio to execute model inference). In our project, `/chat` is a POST request.
*   **PUT**: Used to update or replace an existing resource completely (e.g. modifying an existing candidate record's metadata).
*   **DELETE**: Used to remove a resource permanently from the server.

---

### Question 9: Asynchronous Endpoints (`async def`)
**Question**: Why do we define our API route as `async def chat_with_bot`? What is the advantage of using asynchronous functions in FastAPI?

**Ideal Answer**:
Asynchronous programming in FastAPI allows the server to handle concurrent operations efficiently. 
When the server performs I/O bound tasks (like copying files to the hard drive, reading files, or calling external APIs), standard synchronous code blocks the entire thread, preventing other users from loading pages. 

By using `async def` and `await`, we release control back to FastAPI's event loop during these blocking I/O waits. This allows a single server process to handle hundreds of concurrent candidates uploading audio files simultaneously without blocking the main server thread.

---

### Question 10: Common HTTP Status Codes
**Question**: What are HTTP Status Codes, and what are the most common classes used in REST APIs?

**Ideal Answer**:
HTTP status codes are three-digit numbers returned by the server to communicate the outcome of the request.
*   **200 OK**: Request completed successfully (e.g. successful `/health` response).
*   **201 Created**: Resource created successfully (e.g., saving candidate results).
*   **400 Bad Request**: Client sent invalid input data (e.g., uploading text to an audio-only endpoint).
*   **401 Unauthorized**: Missing or incorrect authentication keys.
*   **404 Not Found**: The requested endpoint URL does not exist.
*   **500 Internal Server Error**: The server code crashed or encountered an unhandled exception (returned in our `except Exception` block in `routes.py`).

---
