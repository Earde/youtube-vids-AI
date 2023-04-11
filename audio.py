import requests


class Audio:
    def __init__(self):
        self.header_eleven_labs = {"xi-api-key": "9716c07f0f50db8c37f3c4212da84e13"}
        self.url_eleven_labs = "https://api.elevenlabs.io/v1/"

    def get(self, text: str, voice_name: str):
        print('Getting Audio...')
        url_voices = self.url_eleven_labs + "voices"

        voices = requests.get(url_voices, headers=self.header_eleven_labs)
        voices = voices.json()["voices"]

        url_tts = None
        for v in voices:
            if v["name"] == voice_name:
                url_tts = self.url_eleven_labs + "text-to-speech/" + v["voice_id"]
                break

        if url_tts is not None:
            data = {
                "text": text,
                "voice_settings": {
                    "stability": 0,
                    "similarity_boost": 0
                }
            }
            audio = requests.post(url_tts, headers=self.header_eleven_labs, json=data)
            audio = audio.content
            with open('audio.wav', mode='bw') as f:
                f.write(audio)

