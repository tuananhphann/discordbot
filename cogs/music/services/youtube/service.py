import json
import logging

from patterns.singleton import SingletonMeta
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from webdriver_manager.firefox import GeckoDriverManager

_log = logging.getLogger(__name__)


class YouTubeService(metaclass=SingletonMeta):

    @staticmethod
    def getPoToken(_: None = None) -> tuple[str, str]:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")

        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()), options=options
        )
        _log.info("YouTube: Getting PoToken...")
        driver.get("https://www.youtube.com/embed/aqz-KE-bpKQ")
        driver.find_element(By.ID, "player").click()
        body = None

        for request in driver.requests:
            if "v1/player" in request.url:
                body = request._body
                break

        if body is not None:
            data = json.loads(body)
            visitorData = data["context"]["client"]["visitorData"]
            poToken = data["serviceIntegrityDimensions"]["poToken"]
        _log.info("YouTube: PoToken is got")
        driver.close()
        return visitorData, poToken
