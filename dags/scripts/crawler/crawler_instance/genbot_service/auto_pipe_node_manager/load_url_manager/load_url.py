# Local Imports
from scripts.crawler.crawler_instance.genbot_service.auto_pipe_node_manager.load_url_manager.load_url_enums import LOAD_URL_RULES
from scripts.crawler.crawler_instance.genbot_service.web_request_handler import webRequestManager
from urllib.parse import urljoin


class load_url:
    __instance = None

    # Initializations
    @staticmethod
    def get_instance():
        if load_url.__instance is None:
            load_url()
        return load_url.__instance

    def __init__(self):
        load_url.__instance = self

    def __get_html(self, p_url):
        return webRequestManager.get_instance().load_url(p_url)

    def on_parse(self, p_request, p_previous_response):

        m_filter_response = []
        m_filter_requests = []
        m_parse_tags = p_request[LOAD_URL_RULES.S_PARSABLE_TAGS]

        for response in p_previous_response:
            if response["name"] in m_parse_tags:
                m_filter_requests.append(response)
            else:
                m_filter_response.append(response)

        m_result = []
        for request in m_filter_requests:
            m_url = urljoin(request["webpage"], request["result"])
            m_redirected_url, status, html = self.__get_html(m_url)
            m_result.append({"name": p_request["data"]["name"], "result": html, "webpage": m_url})
        m_result.extend(m_filter_response)

        return m_result
