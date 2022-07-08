# Local Imports
import os

from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS, RAW_PATH_CONSTANTS
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_MODEL_COMMANDS
from crawler.crawler_instance.genbot_service import genbot_controller
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGO_CRUD
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_services.crawler_services.dynamo_manager.dynamo_controller import dynamo_controller
from crawler.crawler_services.crawler_services.dynamo_manager.dynamo_enums import DYNAMO_CRUD, DYNAMO_COMMANDS


class crawl_model(request_handler):

    # Insert To Database - Insert URL to database after parsing them
    def __init_image_cache(self):
        if not os.path.isdir(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH):
            os.makedirs(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH)
        else:
            helper_method.clear_folder(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH)

    # Start Crawler Manager
    def __install_live_url(self):
        mongo_response = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA, [None], [None]])
        m_live_url_list = []
        for m_url in list(mongo_response):
            m_live_url_list.append(m_url['m_url'])

        m_request_handler, proxies, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])
        m_response = m_request_handler.get(CRAWL_SETTINGS_CONSTANTS.S_START_URL, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies=proxies, allow_redirects=True, )
        m_updated_url_list = []

        for m_server_url in m_response.text.splitlines():
            if helper_method.is_uri_validator(m_server_url) and helper_method.on_clean_url(m_server_url) not in m_live_url_list:
                log.g().s(MANAGE_CRAWLER_MESSAGES.S_INSTALLED_URL + " : " + m_server_url)
                m_server_url = helper_method.on_clean_url(m_server_url)
                mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL, [helper_method.on_clean_url(m_server_url)], [True]])
                m_updated_url_list.append(m_server_url)

        mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_REMOVE_DEAD_CRAWLABLE_URL, [m_live_url_list], [None]])
        return m_live_url_list, m_updated_url_list

    def __reinit_docker_request(self):
        m_live_url_list, m_updated_url_list = self.__install_live_url()
        self.__start_docker_request(m_updated_url_list)

    def __start_docker_request(self, p_fetched_url_list):
        log.g().i(MANAGE_CRAWLER_MESSAGES.S_REINITIALIZING_CRAWLABLE_URL)

        for m_url_node in p_fetched_url_list:
            if APP_STATUS.DOCKERIZED_RUN:
                genbot_controller.celery_genbot_instance.apply_async(
                    args=[m_url_node],
                    kwargs={},
                    queue='genbot_queue', retry=False)

    def __start_direct_request(self, p_fetched_url_list):
        log.g().i(MANAGE_CRAWLER_MESSAGES.S_REINITIALIZING_CRAWLABLE_URL)

        while True:
            for m_url_node in p_fetched_url_list:
                genbot_controller.celery_genbot_instance(m_url_node)
            self.__init_image_cache()
            m_live_url_list, p_fetched_url_list = self.__install_live_url()

    def __on_load_analytics(self):
        m_file = open("analytics.txt", "w")
        response, result = dynamo_controller.get_instance().invoke_trigger(DYNAMO_CRUD.S_READ, [DYNAMO_COMMANDS.S_GET_ALL_ARTICLE, [], [True]])
        m_total_unique_authors = 0
        m_author_name = []
        m_webpage_topic = []
        m_unique_webpage_topic = 0
        m_total_business_topics = 0
        m_total_general_news_topics = 0
        m_total_offensive_images = 0
        m_total_documents = 0
        m_topic_score = {}
        m_author_detail = {}
        m_names_detail = {}

        m_average_yield_score = 0
        m_average_fake_news_positive_score = 0
        m_average_fake_news_negative_score = 0

        for item in result:
            m_total_documents += 1
            m_author = str(item["m_authors"]).replace("By ", "")
            m_webpage_topics_found = str(item["m_webpage_topic"])

            if len(m_author) > 0 and m_author not in m_author_name:
                m_author_name.append(m_author)
                m_total_unique_authors += 1

            if len(m_webpage_topics_found) > 0 and m_webpage_topics_found not in m_webpage_topic:
                m_webpage_topic.append(m_webpage_topics_found)
                m_unique_webpage_topic += 1

            if m_webpage_topics_found not in m_topic_score:
                m_topic_score[m_webpage_topics_found] = 1
            else:
                m_topic_score[m_webpage_topics_found] += 1

            for name in item["m_names"]:
                if name not in m_names_detail:
                    m_names_detail[name] = {}
                    m_names_detail[name]["m_counter"] = 1
                    m_names_detail[name]["m_topic"] = item["m_webpage_topic"]
                else:
                    m_names_detail[name]["m_counter"] += 1
                    if item["m_webpage_topic"] not in m_names_detail[name]["m_topic"]:
                        m_names_detail[name]["m_topic"] += ", " + item["m_webpage_topic"]

            if m_author not in m_author_detail:
                m_author_detail[m_author] = {}
                m_author_detail[m_author]["articles"] = 1
                m_author_detail[m_author]["topic"] = item["m_learned_topic"]
                m_author_detail[m_author]["m_webpage_topic"] = item["m_webpage_topic"]
            else:
                m_author_detail[m_author]["articles"] += 1
                if item["m_learned_topic"] not in m_author_detail[m_author]["topic"]:
                    m_author_detail[m_author]["topic"] += item["m_learned_topic"]
                if item["m_webpage_topic"] not in m_author_detail[m_author]["m_webpage_topic"]:
                    m_author_detail[m_author]["m_webpage_topic"] += ", " + item["m_webpage_topic"]

            if len(str(item["m_fake_news_score_positive"])) > 0:
                if "m_fake_news_score_positive" not in m_author_detail[m_author]:
                    m_author_detail[m_author]["m_fake_news_score_positive"] = float(item["m_fake_news_score_negative"])
                else:
                    m_author_detail[m_author]["m_fake_news_score_positive"] += float(item["m_fake_news_score_negative"])

            if len(str(item["m_fake_news_score_negative"])) > 0:
                if "m_fake_news_score_negative" not in m_author_detail[m_author]:
                    m_author_detail[m_author]["m_fake_news_score_negative"] = float(item["m_fake_news_score_positive"])
                else:
                    m_author_detail[m_author]["m_fake_news_score_negative"] += float(item["m_fake_news_score_positive"])

            m_average_yield_score += int(str(item["m_page_yield_score"]))

            if str(item["m_learned_topic"]) == "business":
                m_total_business_topics += 1

            if str(item["m_learned_topic"]) == "news":
                m_total_general_news_topics += 1

            if item["m_offiensive_images"]:
                m_total_offensive_images += 1

            if len(str(item["m_fake_news_score_positive"])) > 0:
                m_average_fake_news_positive_score += float(str(item["m_fake_news_score_positive"]))
                m_average_fake_news_negative_score += float(str(item["m_fake_news_score_negative"]))

            m_file.write("id : " + str(item["id"]) + "\n")
            m_file.write("url : " + str(item["url"]) + "\n")
            m_file.write("m_text : " + str(item["m_text"]) + "\n")
            m_file.write("m_title : " + str(item["m_title"]) + "\n")
            m_file.write("m_sub_header : " + str(item["m_sub_header"]) + "\n")
            m_file.write("m_date : " + str(item["m_date"]) + "\n")
            m_file.write("m_authors : " + str(item["m_authors"]) + "\n")
            m_file.write("m_fake_news_score_positive : " + str(item["m_fake_news_score_positive"]) + "\n")
            m_file.write("m_fake_news_score_negative : " + str(item["m_fake_news_score_negative"]) + "\n")
            m_file.write("m_page_yield_score : " + str(item["m_page_yield_score"]) + "\n")
            m_file.write("m_content_time : " + str(item["m_content_time"]) + "\n")
            m_file.write("m_learned_topic : " + str(item["m_learned_topic"]) + "\n")
            m_file.write("m_webpage_topic : " + str(item["m_webpage_topic"]) + "\n")
            m_file.write("m_offiensive_images : " + str(item["m_offiensive_images"]) + "\n")
            m_file.write("m_documents : " + str(item["m_documents"]) + "\n")
            m_file.write("m_internal_redirection : " + str(item["m_internal_redirection"]) + "\n")
            m_file.write("m_external_redirection : " + str(item["m_external_redirection"]) + "\n")
            m_file.write("m_video : " + str(item["m_video"]) + "\n")
            m_file.write("m_images_priority : " + str(item["m_images_priority"]) + "\n")
            m_file.write("m_images_references : " + str(item["m_images_references"]) + "\n")
            m_file.write("m_names : " + str(item["m_names"]) + "\n")
            m_file.write("m_emails : " + str(item["m_emails"]) + "\n\n\n")

        m_file.write("\n\n\n*** General Analytics ***\n\n")

        m_file.write("m_total_documents : " + str(m_total_documents) + "\n")
        m_file.write("m_total_unique_authors : " + str(m_total_unique_authors) + "\n")
        m_file.write("m_author_name : " + str(",".join(m_author_name)) + "\n")
        m_file.write("m_unique_webpage_topic : " + str(m_unique_webpage_topic) + "\n")
        m_file.write("m_webpage_topic : " + str(",".join(m_webpage_topic)) + "\n")
        m_file.write("m_total_business_topics : " + str(m_total_business_topics) + "\n")
        m_file.write("m_total_general_news_topics : " + str(m_total_general_news_topics) + "\n")
        m_file.write("m_total_offensive_images : " + str(m_total_offensive_images) + "\n")
        m_file.write("m_average_yield_score : " + str(m_average_yield_score / m_total_documents) + "\n")
        m_file.write("m_average_fake_news_negative_score : " + str(
            m_average_fake_news_negative_score / m_total_documents) + "\n")
        m_file.write("m_average_fake_news_positive_score : " + str(
            m_average_fake_news_positive_score / m_total_documents) + "\n")

        m_file.write("\n\n\n*** Baisness Analytics ***\n\n")

        for key in m_topic_score.keys():
            if len(key) > 0:
                m_file.write(key + " : " + str(m_topic_score[key]) + "\n")

        m_file.write("\n\n\n*** Author Analytics ***\n\n")

        for item in m_author_detail.keys():
            for key in m_author_detail[item].keys():
                if len(item) > 0:
                    if key == "m_fake_news_score_positive" and m_author_detail[item]["articles"] > 0:
                        m_file.write(item + " : " + key + " : " + str(
                            m_author_detail[item][key] / m_author_detail[item]["articles"]) + "\n")
                    elif key == "m_fake_news_score_negative" and m_author_detail[item]["articles"] > 0:
                        m_file.write(item + " : " + key + " : " + str(
                            m_author_detail[item][key] / m_author_detail[item]["articles"]) + "\n")
                    else:
                        m_file.write(item + " : " + key + " : " + str(m_author_detail[item][key]) + "\n")

            m_file.write("\n----------------- \n\n")

        m_file.write("\n\n\n*** Names Analytics ***\n\n")

        for item in m_names_detail.keys():
            m_file.write("name" + " : " + str(item) + "\n")
            for key in m_names_detail[item].keys():
                m_file.write(key + " : " + str(m_names_detail[item][key]) + "\n")
            m_file.write("\n----------------- \n\n")

        m_file.close()

    def __init_crawler(self):
        m_live_url_list, m_updated_url_list = self.__install_live_url()
        m_parsable_url_list = []

        m_parsable_url_list.extend(m_live_url_list)
        m_parsable_url_list.extend(m_updated_url_list)

        if APP_STATUS.DOCKERIZED_RUN:
            self.__start_docker_request(m_parsable_url_list)
        else:
            self.__start_direct_request(m_parsable_url_list)

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == CRAWL_MODEL_COMMANDS.S_INIT:
            self.__init_crawler()
        if p_command == CRAWL_MODEL_COMMANDS.S_LOAD_ANALYTICS:
            self.__on_load_analytics()
