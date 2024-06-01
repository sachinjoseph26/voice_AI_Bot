import assemblyai as ai
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import ollama

class Assistant:
    def __init__(self):
        ai.settings.api_key = "YOUR_ASSEMBLYAI_API_KEY"
        self.client = ElevenLabs(
            api_key = "ELEVENLABS_API_KEY"
        )
        self.transcriber = None
        self.full_transcript = [
            {"role": "system", "content": "Hello, I am your assistant. How can I help you today?"}
        ]


# starting transcription

    def transcription_start(self):
        print(f"\nreal-time transcription: ", end="\r\n")
        self.transcriber = ai.RealtimeTranscriber(
            sample_rate=16_000,
            on_data=self.on_data,
            on_error=self.on_error,
            on_open=self.on_open,
            on_close=self.on_close,
        )
        self.transcriber.connect()

        microphone_stream = ai.extras.MicrophoneStream(sample_rate=16_000)
        self.transcriber.stream(microphone_stream)

    def transcription_close(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None

    def on_open(self, session_opened: ai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        return

    def on_data(self, transcript: ai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, ai.RealtimeFinalTranscript):
            print(transcript.text)
            self.generate_response(transcript)
        else:
            print(transcript.text, end="\r")

    def on_error(self, error: ai.RealtimeError):
        #print("An error occurred:", error)
        return

    def on_close(self):
        #print("Closing Session")
        return


#  real time transcription

    def generate_response(self, transcript):
        self.transcription_close()

        self.full_transcript.append({"role": "user", "content": transcript.text})
        print(f"\nuser: {transcript.text}", end="\r\n")

        ollama_stream = ollama.chat(
            model="llama3",
            messages=self.full_transcript,
            stream=True
        )

        print("Llama 3", end="\r\n")

        text_buffer = ""
        full_text = ""

        for chunk in ollama_stream:
            text_buffer += chunk["message"]["content"]
            if text_buffer.endswith("."):
                audio_stream = self.client.generate(text=text_buffer, model="eleven_turbo_v2", stream=True)
                print(text_buffer, end="\n", flush=True)
                stream(audio_stream)
                full_text += text_buffer
                text_buffer = ""

        if text_buffer:
            audio_stream = self.client.generate(text=text_buffer, model="eleven_turbo_v2", stream=True)
            print(text_buffer, end="\n", flush=True)
            stream(audio_stream)
            full_text += text_buffer

        self.full_transcript.append({"role": "system", "content": full_text})
        self.transcription_start()


# Main
assistant_sj = Assistant()
assistant_sj.transcription_start()
