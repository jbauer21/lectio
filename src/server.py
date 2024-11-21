from flask import Flask, jsonify, request, send_from_directory
from app import download_audio_from_youtube, transcribe_audio, MemoryBuffer, chat_with_gpt

app = Flask(__name__)

# Initialize global variables for transcription and memory buffer
transcription_text = ""
memory_buffer = MemoryBuffer()

# Route to process video URL and transcribe audio
@app.route('/process_video', methods=['POST'])
def process_video():
    global transcription_text
    video_url = request.json.get('url')
    audio_path = download_audio_from_youtube(video_url)
    if audio_path:
        transcription_text = transcribe_audio(audio_path)
        memory_buffer.add_message("system", transcription_text)
        return jsonify({"success": True, "transcription": transcription_text})
    return jsonify({"success": False, "error": "Failed to download or transcribe audio"})

# Route to get transcription text
@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    return jsonify({"transcription": transcription_text})

# Route to handle chat messages
@app.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.json.get('message')
    response = chat_with_gpt(memory_buffer, user_input)
    return jsonify({"response": response})

# Serve the static HTML interface
@app.route('/')
def serve_index():
    return send_from_directory('../html', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
