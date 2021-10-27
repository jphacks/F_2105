from rmn import RMN
import ffmpeg
import os
import cv2
from time import time
from math import ceil
from pprint import pp
import numpy as np
movie_model = RMN()

if __name__ == '__main__':

    names = list('abcd')

    tmp_movie_fname = 'data/meltice-using.mp4'
    cap = cv2.VideoCapture(tmp_movie_fname)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    fers = {name: {emotion: 0 for emotion in emotions}
            for name in names
        } # facial emotion rate

    crop_width  = width - 1680
    crop_height = ceil(crop_width / 16 * 9)
    positions = [
            (range(crop_height*i, crop_height*(i+1)), range(0, crop_width))
            for i in range(len(names))
        ]

    ranges = dict(zip(names, positions))
    ix = 0
    start = time()
    while True:
        ix += 1
        _, img = cap.read()
        if img is None:
            break

        img = img.astype(np.uint8)[:crop_height*len(names), -crop_width:]
        results = movie_model.detect_emotion_for_single_frame(img)
        for result in results:
            xmin, ymin = result['xmin'], result['ymin']
            emotion = result['emo_label']
            for name, (ry, rx) in ranges.items():
                if xmin in rx and ymin in ry:
                    fers[name][emotion] += 1
                    break

        print(f'{ix=}, elapsed={time()-start:4.4f} sec.')
        pp(fers)

