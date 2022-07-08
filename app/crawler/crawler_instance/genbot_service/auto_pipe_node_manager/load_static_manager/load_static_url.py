# Local Imports

from crawler.crawler_instance.genbot_service.auto_pipe_node_manager.load_static_manager.load_static_url_enums import \
    STATIC_URL_RULES, STATIC_URL_DATA_RULES
from crawler.crawler_instance.genbot_service.web_request_handler import webRequestManager


class load_static_url:
    __instance = None

    # Initializations
    @staticmethod
    def get_instance():
        if load_static_url.__instance is None:
            load_static_url()
        return load_static_url.__instance

    def __init__(self):
        load_static_url.__instance = self

    def on_parse(self, p_request, p_previous_response):
        m_redirected_url, status, html = webRequestManager.get_instance().load_url(p_request[STATIC_URL_RULES.S_URL])
        p_previous_response.append({
            "name": p_request[STATIC_URL_RULES.S_DATA][STATIC_URL_DATA_RULES.S_NAME],
            "result": html,
            "webpage": p_request[STATIC_URL_RULES.S_URL]
        })

        return p_previous_response
