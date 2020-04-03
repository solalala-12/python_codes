# Code based on https://github.com/carpedm20/multi-speaker-tacotron-tensorflow


import os
import argparse
from glob import glob
from pydub import silence
from pydub import AudioSegment


'''
* audio 파일을 받아 묵음을 기준으로 audio를 분할하는 소스 / wav - > 1.0001.wav , 1.0002,wav
1. import 정리
2. pydub으로 방법 통일
3. 코드 간소화

'''

def read_audio(audio_path):
    return AudioSegment.from_file(audio_path)

def split_on_silence_with_pydub(

    # 파일 형식 지정 
        audio_path, skip_idx=0, out_ext="wav",
        silence_thresh=-40, min_silence_len=400,
        silence_chunk_len=100, keep_silence=100):
        
    filename = os.path.basename(audio_path).split('.', 1)[0]
    # print('filename : ',filename)

    audio = read_audio(audio_path)
    
    not_silence_ranges = silence.detect_nonsilent(
        audio, min_silence_len=silence_chunk_len,
        silence_thresh=silence_thresh)


    #  파일 별 non_silence 구간 저장
    #  print('not_silence_ranges' ,not_silence_ranges)
    
 

    # 처음 구간
    edges = [not_silence_ranges[0]]

    for idx in range(1, len(not_silence_ranges)-1):
        cur_start = not_silence_ranges[idx][0]
        # 처음 구간의 끝나는 시점
        prev_end = edges[-1][1]

        # 다음 구간 시작점과 전 구간의 끝나는 시작점의 차이가 min_silence_len보다 작다면
        if cur_start - prev_end < min_silence_len:
            # 전구간의 끝지점을 다음구간의 끝지점으로 붙인다. (최소 길이 충족하도록)
            edges[-1][1] = not_silence_ranges[idx][1]
        else:
            edges.append(not_silence_ranges[idx])

    audio_paths = []
    
    for idx, (start_idx, end_idx) in enumerate(edges[skip_idx:]): # skip_idx= 0 (default)
        # 시작 지점이 100ms 보다 이전이면 0을 return
        start_idx = max(0, start_idx - keep_silence)
        
        # 파일의 끝 여유 공간
        end_idx += keep_silence

        # print(start_idx ,end_idx)

        # datasets/kg/0001.0001.wav
        target_audio_path = "{}/{}.{:04d}.{}".format(
                os.path.dirname(audio_path), filename, idx, out_ext)

        # audio 파일 저장
        audio[start_idx:end_idx].export(target_audio_path, out_ext)

        audio_paths.append(target_audio_path)

    return audio_paths

def split_on_silence_batch(audio_paths, **kargv):
    audio_paths.sort()
    print(audio_paths)
    results=[]

    for i in audio_paths:
        print(i,'의 분할을 시작합니다.')
        out = split_on_silence_with_pydub(i)
        results.append(out)

        
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio_pattern', required=True)
    parser.add_argument('--out_ext', default='wav')
    config = parser.parse_args()

    audio_paths = glob(config.audio_pattern)
    # print(audio_paths)

    split_on_silence_batch(
            audio_paths, out_ext=config.out_ext
    )
