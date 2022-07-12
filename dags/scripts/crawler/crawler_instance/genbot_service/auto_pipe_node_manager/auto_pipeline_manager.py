# Local Imports

from scripts.crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS, PIPE_RULES
from scripts.crawler.crawler_instance.genbot_service.auto_pipe_node_manager.load_static_manager.load_static_url import load_static_url
from scripts.crawler.crawler_instance.genbot_service.auto_pipe_node_manager.load_url_manager.load_url import load_url
from scripts.crawler.crawler_instance.genbot_service.auto_pipe_node_manager.parse_manager.parse_html import parse_html
from scripts.crawler.crawler_instance.genbot_service.parse_controller import parse_controller
from scripts.crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class auto_pipeline_manager(request_handler):

    def __init__(self):
        self.__m_html_parser = parse_controller()

    def on_parse_tree(self, p_pipeline):
        m_previous_response = []
        for pipe_node in p_pipeline:
            if pipe_node["command"] == PIPE_RULES.S_LOAD_URL:
                m_previous_response = load_url.get_instance().on_parse(pipe_node, m_previous_response)
            elif pipe_node["command"] == PIPE_RULES.S_PARSE_HTML:
                m_previous_response = parse_html.get_instance().on_parse(pipe_node, m_previous_response)
            elif pipe_node["command"] == PIPE_RULES.S_LOAD_STATIC_URL:
                m_previous_response = load_static_url.get_instance().on_parse(pipe_node, m_previous_response)

    # Wait For Crawl Manager To Provide URL From Queue
    def start_crawler_instance(self, p_request):
        for m_pipeline in p_request:
            self.on_parse_tree(m_pipeline["pipeline"])

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
            self.start_crawler_instance(p_data[0])
