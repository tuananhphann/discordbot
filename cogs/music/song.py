class Song:
    """Song object"""

    def __init__(self, TITLE, URL, CHANNEL, VIEW_COUNT, DURATION, UPLOAD_DATE, THUMBNAIL, YT_URL) -> None:
        self.TITLE = TITLE
        self.URL = URL
        self.CHANNEL = CHANNEL
        self.VIEW_COUNT = VIEW_COUNT
        self.DURATION = DURATION
        self.UPLOAD_DATE = UPLOAD_DATE
        self.THUMBNAIL = THUMBNAIL
        self.YT_URL = YT_URL

    def __str__(self) -> str:
        return f"""
        [{self.TITLE}]({self.YT_URL})
        Channel: {self.CHANNEL}
        Views: {self.VIEW_COUNT}
        Duration: {self.DURATION}
        Upload date: {self.UPLOAD_DATE}
        """

    def info(self):
        "another way to access song info"
        song = {
            'TITLE': self.TITLE,
            'URL': self.URL,
            'CHANNEL': self.CHANNEL,
            'VIEW_COUNT': self.VIEW_COUNT,
            'DURATION': self.DURATION,
            'UPLOAD_DATE': self.UPLOAD_DATE,
            'THUMBNAIL': self.THUMBNAIL,
            'YT_URL': self.YT_URL,
        }
        return song