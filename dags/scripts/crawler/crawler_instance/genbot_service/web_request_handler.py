import urllib3

from bs4 import BeautifulSoup
from scripts.crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from scripts.crawler.constants.keys import TOR_KEYS
from scripts.crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from scripts.crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from scripts.crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from scripts.crawler.crawler_shared_directory.log_manager.log_controller import log
urllib3.disable_warnings()


class webRequestManager:

    def __init__(self):
        pass

    # Load URL - used to request url for parsing to actually crawl the hidden web
    def load_url(self, p_url):

        m_request_handler, proxies, headers = tor_controller.get_instance().invoke_trigger(
            TOR_COMMANDS.S_CREATE_SESSION, [False])

        try:
            page = m_request_handler.get(p_url, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies=proxies, allow_redirects=True, )
            soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), features="lxml")
            if page == "" or page.status_code != 200:
                return p_url, False, page.status_code
            else:
                return page.url, True, str(soup)

        except Exception as ex:
            log.g().e(MANAGE_CRAWLER_MESSAGES.S_WEB_REQUEST_PROCESSING_ERROR + " : " + str(ex))
            return p_url, False, None

    def load_header(self, p_url):
        m_request_handler, proxies, headers = tor_controller.get_instance().invoke_trigger(
            TOR_COMMANDS.S_CREATE_SESSION, [False])

        try:
            headers = {TOR_KEYS.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT}
            page = m_request_handler.head(p_url, headers=headers, timeout=(CRAWL_SETTINGS_CONSTANTS.S_HEADER_TIMEOUT, 27), proxies=proxies, allow_redirects=True, verify=False)
            return True, page.headers

        except Exception:
            log.g().e(MANAGE_CRAWLER_MESSAGES.S_WEB_REQUEST_PROCESSING_ERROR + " : " + str(p_url))
            return False, None

    # Load Header - used to get header without actually downloading the content
    def download_image(self, p_url):
        m_request_handler, proxies, headers = tor_controller.get_instance().invoke_trigger(
            TOR_COMMANDS.S_CREATE_SESSION, [False])

        try:
            response = m_request_handler.get(p_url, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies=proxies, allow_redirects=True, )
            return True, response
        except Exception as ex:
            log.g().e(MANAGE_CRAWLER_MESSAGES.S_WEB_REQUEST_PROCESSING_ERROR + " : " + str(ex))
            return False, None
