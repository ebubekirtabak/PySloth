import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


class SpeechToTextHelpers:

    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/ebubekirtabak/Downloads/Object Detection-7cdcaeea8f25.json"
        print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

    @staticmethod
    def convert_to_text(file_name):
        client = speech.SpeechClient()
        with io.open(file_name, 'rb') as audio_file:
            content = audio_file.read()
            audio = types.RecognitionAudio(content=content)

        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
            sample_rate_hertz=16000,
            language_code='en-US')

        # Detects speech in the audio file
        response = client.recognize(config, audio)
        for result in response.results:
            print('Transcript: {}'.format(result.alternatives[0].transcript))

        return result.alternatives[0].transcript
