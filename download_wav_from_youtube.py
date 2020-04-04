import os
import youtube_dl
import csv
import subprocess

'''
* youtube에서 data lownload 
metadata.csv
title|url|start_point|end_point
'''





base_dir = os.path.dirname(os.path.realpath(__file__))


def get_mili_sec(text):
    minute, second = text.strip().split(':')
    return (int(minute) * 60 + int(second)) * 1000

class Data(object):
    def __init__(
            self, title, video_url, start_time, end_time):
        self.video_url = video_url
        self.title = title
        self.start =start_time
        self.end = end_time
def read_csv(path):
    # print(path)
    title_num=0
    with open(path,'r',encoding='utf-8') as f:
        data = []
        for line in f:
            title_num+=1
            title, video_url, start_time, end_time = line.split('|')

            data.append(Data(title, video_url, start_time, end_time))
        return data


def download_audio_with_urls(data, out_ext="wav"):
    for d in data:
        original_path='./audio/'+d.title+'.original.mp3'
        out_path='./audio/'+d.title+'.wav'


        options = {
            'format': 'bestaudio/best',
            'outtmpl': original_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': "mp3",
                'preferredquality': '320',
            }],
        }

        try:
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([d.video_url])
                print('Complete download!')

        except Exception as e:
            print('error',e)


        # mp3 file에서 원하는 만큼 자르고 wav파일로 저장
        #  ffmpeg -i test.mp3 -ss 00:00:00 -to 00:00:30  temp.wav

        print(original_path,out_path)

        texts='ffmpeg -i {} -ss {} -to {}  {}'.format(original_path,
        "%02d:%02d:%02d" % (0, int(d.start.split(':')[0]), int(d.start.split(':')[1])),"%02d:%02d:%02d" % (0, int(d.end.split(':')[0]), int(d.end.split(':')[1])),out_path)
        # print(texts)
        subprocess.call(texts,shell=True)
        os.remove(original_path)
        
        
if __name__ == '__main__':
    if not os.path.exists(os.path.join(base_dir, "audio")):
        os.makedirs(os.path.join(base_dir, "audio"))

    data = read_csv(os.path.join(base_dir, "metadata.txt"))
    download_audio_with_urls(data)

