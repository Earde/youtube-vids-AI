import utils
import pandas as pd


class Transcribe:
    def __init__(self):
        self.headers = {"Authorization": "ba82971c8cdd4c399d75f61cdbb1f977",
                        "Content-Type": "application/json"}
        self.endpoint = "https://api.assemblyai.com/v2/transcript"

    def get(self):
        print('Getting Transcriptions...')
        upload_url = utils.upload_file('audio.wav', self.headers)

        transcript_response = utils.request_transcript(upload_url, self.headers)
        polling_endpoint = utils.make_polling_endpoint(transcript_response)
        utils.wait_for_completion(polling_endpoint, self.headers)
        paragraphs = utils.get_paragraphs(polling_endpoint, self.headers)

        paragraphs_arr = []
        for para in paragraphs:
            for word in para['words']:
                d = {
                    'start': int(word['start']),
                    'end': int(word['end']),
                    'text': word['text']
                }
                paragraphs_arr.append(d)
        paragraphs_df = pd.DataFrame(data=paragraphs_arr)

        return paragraphs_df
