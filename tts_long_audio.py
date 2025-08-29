import sys
import os
from dotenv import load_dotenv
from google.cloud import texttospeech_v1beta1 as texttospeech

def synthesize_long_audio(text, output_gcs_uri, speaking_rate=1.0, input_gcs_uri=None):
    client = texttospeech.TextToSpeechLongAudioSynthesizeClient()
    load_dotenv()
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("GCP_PROJECT_ID not found in environment. Please set it in .env file.")
        sys.exit(1)

    parent = f"projects/{project_id}/locations/us-central1"
    input_config = texttospeech.SynthesisInput(text=text)
    voice_name = os.getenv("TTS_VOICE_NAME", "en-US-Wavenet-D")
    print(f"Using voice: {voice_name}")
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=speaking_rate
    )
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name
    )
    if input_gcs_uri:
        input_config = texttospeech.SynthesisInput(ssml_gcs_uri=input_gcs_uri)

    request = texttospeech.SynthesizeLongAudioRequest(
        parent=parent,
        input=input_config,
        audio_config=audio_config,
        output_gcs_uri=output_gcs_uri,
        voice=voice
    )
    operation = client.synthesize_long_audio(request=request)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=1800)
    print(f"Audio content written to {output_gcs_uri}")

def main():
    load_dotenv()
    bucket = os.getenv("OUTPUT_GCS_BUCKET")
    if not bucket:
        print("OUTPUT_GCS_BUCKET not found in environment. Please set it in .env file.")
        sys.exit(1)

    speaking_rate = 1.0
    env_rate = os.getenv("TTS_SPEAKING_RATE")
    if env_rate:
        try:
            speaking_rate = float(env_rate)
        except ValueError:
            print("Invalid TTS_SPEAKING_RATE in environment. Must be a float between 0.25 and 2.0. Using default 1.0.")
            speaking_rate = 1.0

    speaking_rate = max(0.25, min(2.0, speaking_rate))

    if len(sys.argv) < 2:
        print("Usage: python tts_long_audio.py text_file_to_synthesize.txt")
        sys.exit(1)

    file_name = sys.argv[1]
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    output_gcs_uri = f"gs://{bucket}/{os.path.splitext(os.path.basename(file_name))[0]}.wav"
    synthesize_long_audio(text, output_gcs_uri, speaking_rate)

if __name__ == "__main__":
    main()
