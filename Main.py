import os
from CaptionInformation import *
from Movie import *
from DB import *
import math

# xx:xx:xx --> xx:xx:xx 형식의 문자열을 [시작시간, 종료시간] 형태로 만들어 주는 함수
def timeAnalysis(timeInfo, plus_time, minus_time):
    timeInfo = timeInfo.strip(" ")
    startTime = timeInfo.split("-->")[0].strip(" ").split(",")[0] # 자막 시작 시간
    endTime = timeInfo.split("-->")[1].strip(" ").split(",")[0]  # 자막 종료 시간

    hour = int(startTime.split(":")[0]) * 3600
    minute = int(startTime.split(":")[1]) * 60
    second = int(startTime.split(":")[2])
    startSecond = hour + minute + second - 1 + plus_time - minus_time

    hour = int(endTime.split(":")[0]) * 3600
    minute = int(endTime.split(":")[1]) * 60
    second = int(endTime.split(":")[2])
    endSecond = hour + minute + second + 1 + plus_time - minus_time

    return [startSecond, endSecond]

def fileOpen(name):
    fileName = name.split(".")[0]
    file = open(name, "r", encoding="UTF8")
    lines = file.readlines()
    file.close()

    temp = ""
    captionList = []
    #자막 파일 첫줄엔 영화 제목, 자막 딜레이 값이 들어가있다
    first_info = lines[0]
    first_info = first_info.split(',')
    #영화 한글, 영어 제목 체크
    k_title = first_info[0]
    e_title = first_info[1]
    #자막 딜레이 체크
    plus_time = int(first_info[2])
    minus_time = int(first_info[3])
    del lines[0]

    for n in lines:
        if n == '\n':
            captionList.append(temp.strip('\n').split("\n"))
            temp = ""
        temp += n

    captionInfoList = []
    for captionInfo in captionList:
        #자막
        num = (captionInfo[0].strip(" "))
        #자막 재생 시간을 구한다
        timeInfo = timeAnalysis(captionInfo[1].strip(" "), plus_time, minus_time)
        #자막 내용을 구한다
        captionStr = ""
        for temp in captionInfo[2:]:
            captionStr += temp + " "
        caption = captionStr.strip(" ")
        captionInfoList.append(CaptionInformation( num, timeInfo, caption))

    movie = Movie(k_title, e_title, captionInfoList)
    return movie



curlist = os.listdir()
for filename in curlist:
    if filename.find(".srt") > -1:
        #파일 이름으로 영화 정보 가져옴
        movie = fileOpen(filename)
        #영화 자막 파일 분리
        captionInfoList = movie.captionInfoList
        #자막 길이별로 정렬
        captionInfoList.sort(key = lambda x : len(x.caption))
        #DB 접속
        db = MemorizeDB('root', 'dlflrh18', '127.0.0.1')
        db.connect()

        #DB에 영화 정보 insert
        db.insertMovie(movie.k_title, movie.e_title)
        #영화 제목으로 영화 번호값을 얻는다
        movie_id = db.getMovieIdByk_title(k_title=movie.k_title)

        for captionInfo in captionInfoList[math.ceil(len(captionInfoList)/2):]:
            captionInfo.movie_id = movie_id
            db.insertCaption(captionInfo)
            print('['+movie.e_title+'] '+ '[' + str(captionInfo.startSecond)+':'+str(captionInfo.endSecond)+'] :'+captionInfo.caption)
        db.dbClose()