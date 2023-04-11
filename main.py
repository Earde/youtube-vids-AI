from os.path import isfile

import numpy as np
import pandas as pd
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip

from audio import Audio
from transcribe import Transcribe
import cv2


def second_to_timecode(x: float) -> str:
    hour, x = divmod(x, 3600)
    minute, x = divmod(x, 60)
    second, x = divmod(x, 1)
    millisecond = int(x * 1000.)

    return '%.2d:%.2d:%.2d,%.3d' % (hour, minute, second, millisecond)


def to_srt(
        words,
        endpoint_sec=0.5,
        length_limit=16) -> str:
    def _helper(end: int) -> None:
        lines.append("%d" % section)
        lines.append(
            "%s --> %s" %
            (
                second_to_timecode(words[start]['start']),
                second_to_timecode(words[end]['end'])
            )
        )
        lines.append(' '.join(x['text'] for x in words[start:(end + 1)]))
        lines.append('')

    lines = list()
    section = 0
    start = 0
    for k in range(1, len(words)):
        if ((words[k]['start'] - words[k - 1]['end']) >= endpoint_sec) or \
                (length_limit is not None and (k - start) >= length_limit) or \
                ('.' in words[k - 1]['text']):
            _helper(k - 1)
            start = k
            section += 1
    _helper(len(words) - 1)

    extra = lines[-3]
    lines.append("%d" % (section + 1))
    lines.append(extra)

    return '\n'.join(lines)


if __name__ == '__main__':
    text = "Once upon a time, there was a boy. " \
           "He enjoyed pea soup, and also soy. " \
           "He pissed off a roof, and then off a tree. " \
           "To be the biggest worm-pee man the world's ever seen."
    voice_name = "Bella"

    if not isfile('audio.wav'):
        audio = Audio()
        audio.get(text=text, voice_name=voice_name)

    if not isfile('paragraphs.csv'):
        transcribe = Transcribe()
        paragraphs_df = transcribe.get()
        paragraphs_df.to_csv('paragraphs.csv', sep=';', index=False)
    else:
        paragraphs_df = pd.read_csv('paragraphs.csv', delimiter=';')

    print('Getting SRT...')
    words = []
    for index, row in paragraphs_df.iterrows():
        d = {
            'start': row['start'] / 1000.0,
            'end': row['end'] / 1000.0,
            'text': row['text']
        }
        words.append(d)

    srt = to_srt(words=words)
    with open('subs.srt', "w") as f:
        f.write(srt)

    print('Getting Video...')
    width = 1600
    height = 900

    frame_rate = 30
    frame_ms = 1000 / frame_rate

    video_duration = paragraphs_df['end'].max() + 2000

    out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'MP4V'), frame_rate, (width, height))
    for i in range(0, int(video_duration / frame_ms)):
        frame = np.zeros((height, width, 3), np.uint8)
        out.write(frame)
    out.release()

    generator = lambda txt: TextClip(txt, font='Arial', fontsize=30, color='white')
    subs = SubtitlesClip("subs.srt", generator)
    subtitles = SubtitlesClip(subs, generator)

    video_clip = VideoFileClip('output.mp4')
    result = CompositeVideoClip([video_clip, subtitles.set_pos(('center', 'bottom'))])

    audio_clip = AudioFileClip('audio.wav')
    new_audioclip = CompositeAudioClip([audio_clip])
    result.audio = new_audioclip

    result.write_videofile('output.mp4', fps=frame_rate, threads=1, codec='libx264')
