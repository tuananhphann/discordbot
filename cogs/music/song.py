from discord.ext import commands

class Song:
    """
    Song object

    property:
        TITLE       (str): Title of this song.
        URL         (str): URL to the audio source of this song.
        CHANNEL     (str): The name of the channel that uploaded this song.
        VIEW_COUNT  (str): views of this song. Seperated by ','.
        DURATION    (str): length of this song. Format '%H:%M:%S'.
        UPLOAD_DATE (str): The time the song was uploaded. Format '%d/%m/%Y'.
        THUMBNAIL   (str): URL to the thumbnail.
        YT_URL      (str): Direct URL to this song's Youtube page.
        CTX         (discord.ext.commands.Context): Context
    
    method:
        info (dict): Returns the entire property but as a dict.
    """

    def __init__(self, TITLE: str, URL: str, CHANNEL: str, VIEW_COUNT: str, DURATION: str, UPLOAD_DATE: str, THUMBNAIL: str, YT_URL: str, CTX: commands.Context) -> None:
        self.TITLE: str = TITLE
        self.URL: str = URL
        self.CHANNEL: str = CHANNEL
        self.VIEW_COUNT: str = VIEW_COUNT
        self.DURATION: str = DURATION
        self.UPLOAD_DATE: str = UPLOAD_DATE
        self.THUMBNAIL: str = THUMBNAIL
        self.YT_URL: str = YT_URL
        self.CTX = CTX

    def __str__(self) -> str:
        return f"""
        [{self.TITLE}]({self.YT_URL})
        Channel: {self.CHANNEL}
        Views: {self.VIEW_COUNT}
        Duration: {self.DURATION}
        Upload date: {self.UPLOAD_DATE}
        """

    def info(self) -> dict[str, str]:
        "another way to access song info"
        song: dict[str, str] = {
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