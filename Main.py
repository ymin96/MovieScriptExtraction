import os
from CaptionInformation import *
from Movie import *
from DB import *
import mysql_auth
import math
import re
import numpy as np
import cv2


# xx:xx:xx --> xx:xx:xx 형식의 문자열을 [시작시간, 종료시간] 형태로 만들어 주는 함수
def timeAnalysis(timeInfo, plus_time, minus_time):
    timeInfo = timeInfo.strip(" ")
    startTime = timeInfo.split("-->")[0].strip(" ").split(",")[0]  # 자막 시작 시간
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


# 자막 정보를 받아 movie 객체를 반환해준다.
def getMovieObject(name):
    fileName = name.split(".")[0]
    file = open(name, "r", encoding="UTF8")
    lines = file.readlines()
    file.close()

    temp = ""
    captionList = []
    # 자막 파일 첫줄엔 영화 제목, 자막 딜레이 값이 들어가있다
    first_info = lines[0]
    first_info = first_info.split(',')
    # 영화 한글, 영어 제목 체크
    k_title = first_info[0]
    e_title = first_info[1]
    # 자막 딜레이 체크
    plus_time = int(first_info[2])
    minus_time = int(first_info[3])
    # 영화 포스터 링크
    thumbnail = first_info[4]
    del lines[0]

    for n in lines:
        if n == '\n':
            captionList.append(temp.strip('\n').split("\n"))
            temp = ""
        temp += n

    captionInfoList = []
    for captionInfo in captionList:
        # 자막 넘버
        num = (captionInfo[0].strip(" "))
        # 자막 재생 시간을 구한다
        timeInfo = timeAnalysis(captionInfo[1].strip(" "), plus_time, minus_time)
        # 자막 내용을 구한다
        captionStr = ""
        for temp in captionInfo[2:]:
            captionStr += temp + " "
        caption = captionStr.strip(" ")
        # 자막 리스트에 자막 추가
        captionInfoList.append(CaptionInformation(num, timeInfo, caption))

    # 자막 길이별로 정렬
    captionInfoList.sort(key=lambda x: len(x.caption))

    # 자막에 정규식 패턴 적용
    shortCaptionList = []
    pattern = re.compile('[a-zA-Z. ]+')
    for captionInfo in captionInfoList[math.ceil(len(captionInfoList) / 1.5):]:
        # 정규식 검사
        match = pattern.fullmatch(captionInfo.caption)
        if match:
            # [.] 제거
            captionInfo.caption = captionInfo.caption.replace('.', '')
            shortCaptionList.append(captionInfo)

    movie = Movie(k_title, e_title, shortCaptionList, thumbnail)
    return movie


def insertMovie(movie, db):
    # DB에 영화 정보 insert
    db.insertMovie(movie)
    # 영화 제목으로 영화 번호값을 얻는다
    movie_id = db.getMovieIdByk_title(k_title=movie.k_title)

    # DB에 자막 정보 저장
    for captionInfo in movie.captionInfoList:
        captionInfo.movie_id = movie_id
        db.insertCaption(captionInfo)
        print(movie.e_title + ": [" + str(captionInfo.startSecond) + "] [" + str(
            captionInfo.endSecond) + "] - " + captionInfo.caption)


def makeStillCutImage(movie, movie_folder_name ,onlyMainStillCut=False):
    # 영화 객체 가져오기
    videoObj = cv2.VideoCapture(movie.filepath)

    # 영화의 프레임
    fps = videoObj.get(cv2.CAP_PROP_FPS)

    frameCount = 0

    for captionInfo in movie.captionInfoList:
        # 자막 시작점의 화면 가져오기
        videoObj.set(cv2.CAP_PROP_POS_FRAMES, fps * captionInfo.startSecond)

        ret, frame = videoObj.read()

        # 썸네일 크기 조정 16:9
        resizeImage = cv2.resize(frame, (228, 128))
        # 썸네일 저장
        cv2.imwrite("./thumbnail/%d.jpg" % frameCount, resizeImage)
        # 자막 정보에 썸네일 경로 입력
        captionInfo.thumbnail = (movie_folder_name + "/thumbnail/" + str(frameCount) + ".jpg")
        frameCount += 1

    return movie


curlist = os.listdir()
os.chdir('./Movie')
movie_folders = os.listdir()

# DB 접속 정보
login = mysql_auth.Info
# DB 접속
db = MemorizeDB(login["user"], login["passwd"], login["host"])
db.connect()

for movie_folder in movie_folders:
    os.chdir('./' + movie_folder)
    files = os.listdir()
    movie = None
    filepath = None
    # DB에 영화가 존재한다면 return
    if db.checkMovieByE_title(movie_folder):
        break
    # 폴더 순회하며 자막파일과 영화 데이터 가져옴
    for file in files:
        if file.find(".srt") > -1:
            # 파일 이름으로 영화 정보 가져옴
            movie = getMovieObject(file)
        elif file.find(".webm") > -1:
            filepath = os.getcwd() + '/' + file
            filepath = filepath.replace('\\', '/')
    movie.filepath = filepath
    # 썸네일 이미지 추출
    makeStillCutImage(movie, movie_folder)
    insertMovie(movie, db)
    os.chdir('../')
db.dbClose()
