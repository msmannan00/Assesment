# Local Imports
from crawler.crawler_instance.genbot_service.auto_pipe_node_manager.load_static_manager.load_static_url_enums import STATIC_URL_DATA_RULES
from crawler.crawler_instance.genbot_service.auto_pipe_node_manager.parse_manager.parse_html_enums import PARSE_HTML_RULES
from bs4 import BeautifulSoup


class parse_html:
    __instance = None

    # Initializations
    @staticmethod
    def get_instance():
        if parse_html.__instance is None:
            parse_html()
        return parse_html.__instance

    def __init__(self):
        parse_html.__instance = self

    def get_tag_result(self, html, p_filter):
        soup = BeautifulSoup(html, "html.parser")

        if p_filter["content"] != "text":
            results = []
        else:
            results = ""

        if p_filter["type"] == "property":
            response = soup.find_all(p_filter["tag"], {p_filter["filter_name"]: p_filter["value"]})
            for item in response:
                if p_filter["content"] != "text":
                    results.append(item.get(p_filter["content"]))
                else:
                    results += item.text

        if p_filter["type"] == "tag":
            response = soup.find_all(p_filter["tag"])
            for item in response:
                if p_filter["content"] != "text":
                    results.append(item.get(p_filter["content"]))
                else:
                    results += item.text

        if p_filter["content"] != "text":
            return results
        else:
            return [results]

    def invoke_parser(self, html, data, webpage):
        m_result = []
        for tag in data["filter"]:
            response = self.get_tag_result(html, tag)
            m_result.extend(response)

        m_response = []
        for item in m_result:
            m_response.append({"name": data[STATIC_URL_DATA_RULES.S_NAME], "result": item, "webpage": webpage})

        return m_response

    def on_parse(self, p_request, p_previous_response):
        m_filter_response = []
        m_filter_requests = []
        m_parse_tags = p_request[PARSE_HTML_RULES.S_PARSABLE_TAGS]

        for response in p_previous_response:
            if response["name"] in m_parse_tags:
                m_filter_requests.append(response)
            else:
                m_filter_response.append(response)

        m_parsed_results = []

        for m_requests in m_filter_requests:
            m_group_result = []
            for data in p_request["data"]:
                m_group_result.extend(self.invoke_parser(m_requests["result"], data, m_requests["webpage"]))

            if p_request[PARSE_HTML_RULES.S_RETURN_COLLECTION_TYPE] == "list":
                m_parsed_results.extend(m_group_result)
            else:
                m_parsed_results.append(m_group_result)

        m_parsed_results.extend(m_filter_response)
        return m_parsed_results
