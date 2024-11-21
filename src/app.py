# app.py
import openai
import os
import re
import yt_dlp

# Set your OpenAI API key here
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to download audio from YouTube using yt_dlp with error handling
def download_audio_from_youtube(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
        return file_path
    except yt_dlp.utils.DownloadError as e:
        print(f"Error: Failed to download the video. Please check the URL.\nDetails: {e}")
    except Exception as e:
        print(f"Unexpected error during download: {e}")
    return None


# Function to transcribe audio using the OpenAI API with error handling
def transcribe_audio(audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            transcription_response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
        transcription = transcription_response['text']

        # Format transcription by adding newlines between sentences
        formatted_transcription = format_transcription(transcription)

        os.remove(audio_path)  # Clean up audio file after transcription
        return formatted_transcription
    except FileNotFoundError:
        print("Error: Audio file not found. Ensure the file path is correct.")
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error during transcription: {e}")
    except Exception as e:
        print(f"Unexpected error during transcription: {e}")
    return None

# Function to format transcription by adding newlines after sentences
def format_transcription(text):
    # Use regex to identify sentence boundaries and add a newline
    formatted_text = re.sub(r'(?<=[.?!])\s+', '\n\n', text)
    return formatted_text

# Initialize conversational memory buffer
class MemoryBuffer:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_conversation(self):
        return self.messages

# Chatbot function using GPT-4 with error handling
def chat_with_gpt(memory_buffer, user_input):
    memory_buffer.add_message("user", user_input)
    
    # Filter out messages with None content
    conversation_history = [
        msg for msg in memory_buffer.get_conversation()
        if msg['content'] is not None
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=conversation_history
        )
        assistant_message = response['choices'][0]['message']['content']
        memory_buffer.add_message("assistant", assistant_message)
        return assistant_message
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error during chat: {e}")
    except Exception as e:
        print(f"Unexpected error during chat: {e}")
    return "Sorry, there was an error processing your request."



if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    audio_path = download_audio_from_youtube(video_url)
    if audio_path:
        transcription = transcribe_audio(audio_path)
    else:
        print("Failed to download or process audio. Please try again.")