const micBtn = document.getElementById('micBtn');
const chatArea = document.getElementById('chatArea');
const audioPlayer = document.getElementById('audioPlayer');

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// Append a message to the chat UI
function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.innerText = text;
    chatArea.appendChild(msgDiv);
    chatArea.scrollTop = chatArea.scrollHeight; // Auto-scroll to bottom
}

// Request permission to use the user's microphone when page loads
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        
        // As you speak, collect the audio data chunks
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        // When you hit stop, package it up and send to the API!
        mediaRecorder.onstop = async () => {
            // Package the audio into a single Blob (virtual file)
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            audioChunks = []; // Reset chunks for next recording
            
            // Build the form-data (Exactly what Swagger UI did behind the scenes!)
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'live_voice.wav');

            appendMessage("Thinking...", "system");

            try {
                // Shoot the raw audio over to our Python FastAPI Backend!
                const response = await fetch('http://127.0.0.1:8000/chat', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();

                if (data.success) {
                    appendMessage(`You said: "${data.user_said}"`, "user");
                    appendMessage(`AI Screener: ${data.bot_reply}`, "system");
                    
                    // The API created 'response_live_voice.wav.mp3'. 
                    // Let's ask the `<audio>` tag in our HTML to fetch it and play it out loud!
                    audioPlayer.src = `http://127.0.0.1:8000/audio/response_live_voice.wav.mp3?cachebuster=${new Date().getTime()}`;
                    audioPlayer.play();
                } else {
                    appendMessage(`Error: ${data.error}`, "error");
                }

            } catch (error) {
                appendMessage("Failed to connect to the server. Is Uvicorn running?", "error");
                console.error(error);
            }
        };
    })
    .catch(err => {
        console.error("Microphone access denied: ", err);
        appendMessage("Microphone access denied. Please allow site permissions.", "error");
    });

// Handle the glowing Mic Button Click
micBtn.addEventListener('click', () => {
    if (!mediaRecorder) return;

    if (!isRecording) {
        // Start Recording!
        mediaRecorder.start();
        isRecording = true;
        micBtn.classList.add('recording');
        chatArea.innerHTML = ''; // Clear chat area
        appendMessage("Listening... click the mic again when done.", "system");
    } else {
        // Stop Recording!
        mediaRecorder.stop();
        isRecording = false;
        micBtn.classList.remove('recording');
    }
});
