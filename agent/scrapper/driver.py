import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .utils import logger


class ScaperWebDriver:

    instance = None
    last_start_time = None

    def __init__(self):
        self.driver = None

    def _start_driver(self) -> None:
        if not self.instance:
            logger.info("[Starting Web Driver]")
            chrome_options = Options()
            chrome_options.add_argument("--log-level=1")
            chrome_options.add_argument("--headless")  # Run in headless mode

            self.instance = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=chrome_options
            )
            self.instance.maximize_window()
            self.last_start_time = datetime.datetime.now()

        self.driver = self.instance

    def __quit(self):
        if self.instance:
            self.instance.quit()
            self.instance = None

    def _close_driver(self) -> None:
        logger.info("[Quiting Web Driver]")

        now = datetime.datetime.now()

        print(
            "[TIME Remaining]: {}".format(
                ((now - self.last_start_time).total_seconds() / 60)
            )
        )
        # self.driver.quit()

    def __getitem__(self, key):
        if key == "driver":
            return self.instance
