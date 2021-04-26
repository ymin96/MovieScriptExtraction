class CaptionInformation:

    def __init__(self, num, timeInfo, caption):
        self.num = num
        self.startSecond = timeInfo[0]
        self.endSecond = timeInfo[1]
        self.caption = caption
        self.movie_id = -1