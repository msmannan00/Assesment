# Local Imports

from eventlet import sleep
from raven.transport import requests
from scripts.crawler.constants.app_status import APP_STATUS
from scripts.crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS, NETWORK_MONITOR
from scripts.crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from scripts.crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_CONTROLLER_COMMANDS, CRAWL_MODEL_COMMANDS
from scripts.crawler.crawler_instance.crawl_controller.crawl_model import crawl_model
from scripts.crawler.crawler_instance.tor_controller.tor_enums import TOR_STATUS
from scripts.crawler.crawler_services.helper_services.scheduler import RepeatedTimer
from scripts.crawler.crawler_shared_directory.log_manager.log_controller import log
from scripts.crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from scripts.crawler.shared_data import celery_shared_data


class crawl_controller(request_handler):

    # Local Variables
    __m_crawl_model = None

    # Initializations
    def __init__(self):
        self.__m_crawl_model = crawl_model()

    def __update_crawler_status(self):
        try:
            requests.get(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_STATUS_URL, timeout=100)
        except Exception:
            pass

    def __update_internet_status(self):
        url = NETWORK_MONITOR.S_PING_URL
        timeout = 5
        try:
            requests.head(url, timeout=timeout)
            celery_shared_data.get_instance().set_network_status(True)
        except Exception:
            celery_shared_data.get_instance().set_network_status(False)
            log.g().w(MANAGE_CRAWLER_MESSAGES.S_INTERNET_CONNECTION_ISSUE)

    def __wait_for_tor(self):
        while APP_STATUS.S_TOR_STATUS != TOR_STATUS.S_RUNNING:
            sleep(10)
            continue

    def __on_init(self):
        self.__wait_for_tor()
        self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_INIT)

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == CRAWL_CONTROLLER_COMMANDS.S_RUN_CRAWLER:
            self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_RUN_CRAWLER)
        if p_command == CRAWL_CONTROLLER_COMMANDS.S_INIT_CRAWLER:
            self.__on_init()
        if p_command == CRAWL_CONTROLLER_COMMANDS.S_LOAD_ANALYTICS:
            self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_LOAD_ANALYTICS)
        if p_command == CRAWL_CONTROLLER_COMMANDS.S_LOAD_ANALYTICS_WEEKLY:
            self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_LOAD_ANALYTICS_WEEKLY)
