# Local Imports
import datetime
import mimetypes
import pathlib
import re
import string

import requests
import validators

from urllib.parse import urljoin
from abc import ABC
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from thefuzz import fuzz
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.strings import STRINGS
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.genbot_service.genbot_enums import PARSE_TAGS
from crawler.crawler_instance.local_shared_model.article_model import article_model
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_controller import topic_classifier_controller
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS
from crawler.crawler_services.helper_services.spell_check_handler import spell_checker_handler
import nltk

nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')

# class to parse html raw duplicationHandlerService


class html_parse_manager(HTMLParser, ABC):


    def __init__(self, m_base_url, m_html, p_depth):
        super().__init__()
        self.m_depth = p_depth
        self.m_html = m_html
        self.m_base_url = m_base_url
        self.m_article_model = article_model()
        self.m_title = STRINGS.S_EMPTY
        self.m_meta_description = STRINGS.S_EMPTY
        self.m_meta_content = STRINGS.S_EMPTY
        self.m_important_content = STRINGS.S_EMPTY
        self.m_important_content_raw = []
        self.m_content = STRINGS.S_EMPTY
        self.m_meta_keyword = STRINGS.S_EMPTY
        self.m_content_type = CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL
        self.m_sub_url = []
        self.m_image_url = []
        self.m_doc_url = []
        self.m_video_url = []

        self.m_paragraph_count = 0
        self.m_parsed_paragraph_count = 0
        self.m_query_url_count = 0
        self.m_non_important_text = STRINGS.S_EMPTY
        self.rec = PARSE_TAGS.S_NONE
        self.all_url_count = 0

    # find url type and populate the list respectively

    def __insert_external_url(self, p_url):
        self.all_url_count += 1
        if p_url is not None and not str(p_url).__contains__("#"):
            mime = mimetypes.MimeTypes().guess_type(p_url)[0]
            if 5 < len(p_url) <= CRAWL_SETTINGS_CONSTANTS.S_MAX_URL_SIZE:

                # Joining Relative URL
                if not p_url.startswith("https://") and not p_url.startswith("http://") and not p_url.startswith(
                        "ftp://"):
                    m_temp_base_url = self.m_base_url
                    p_url = urljoin(m_temp_base_url, p_url)
                    p_url = p_url.replace(" ", "%20")
                    p_url = helper_method.on_clean_url(helper_method.normalize_slashes(p_url))

                if validators.url(p_url):
                    suffix = ''.join(pathlib.Path(p_url).suffixes)
                    m_host_url = helper_method.get_host_url(p_url)
                    m_parent_url = helper_method.get_host_url(self.m_base_url)
                    if mime is None:
                        mime = mimetypes.MimeTypes().guess_type(p_url)[0]
                    if mime is not None and mime != "text/html":
                        if suffix in CRAWL_SETTINGS_CONSTANTS.S_DOC_TYPES and len(self.m_doc_url) < 10:
                            self.m_doc_url.append(p_url)
                        elif str(mime).startswith("video") and len(self.m_video_url) < 10:
                            self.m_video_url.append(p_url)
                    elif m_host_url.__eq__(m_parent_url):
                        if m_host_url.__contains__("?") and self.m_query_url_count < 5:
                            self.m_query_url_count += 1
                            self.m_sub_url.append(helper_method.normalize_slashes(p_url))
                        else:
                            self.m_sub_url.append(helper_method.normalize_slashes(p_url))
                    elif "bbc" not in p_url:
                        self.m_article_model.m_external_redirection.append(p_url)

    def handle_starttag(self, p_tag, p_attrs):
        if p_tag == "a":
            # gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-pica-bold nw-o-link-split__anchor
            # 'nw-o-link-split__anchor gs-u-pt- gs-u-pb- gs-u-display-block nw-o-link-split__text'
            for name, value in p_attrs:
                if name == "href":
                    for item in p_attrs:
                        if item[0] == "class" and (item[1] == "gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-pica-bold nw-o-link-split__anchor" or item[1] == "nw-o-link-split__anchor gs-u-pt- gs-u-pb- gs-u-display-block nw-o-link-split__text"):
                            self.__insert_external_url(value)
                if p_attrs[0][1] == "ssrcss-2kny4l-ContributorLink e5xb54n0":
                    self.rec = PARSE_TAGS.S_ARTICLE_AUTHOR
                    return

        if p_tag == 'img':
            for value in p_attrs:
                if value[0] == 'src' and not helper_method.is_url_base_64(value[1]) and len(self.m_image_url) < 35:
                    # Joining Relative URL
                    if len(p_attrs) > 1 and p_attrs[1][1] == "ssrcss-evoj7m-Image ee0ct7c0":
                        try:
                            if p_attrs[3][1] == "eager":
                                self.m_article_model.m_images_priority.append(value[1])
                            elif int(p_attrs[6][1]) > 900:
                                self.m_article_model.m_images_references.append(value[1])
                        except Exception:
                            pass

                    m_temp_base_url = self.m_base_url
                    if not m_temp_base_url.endswith("/"):
                        m_temp_base_url = m_temp_base_url + "/"
                    m_url = urljoin(m_temp_base_url, value[1])
                    m_url = helper_method.on_clean_url(helper_method.normalize_slashes(m_url))
                    self.m_image_url.append(m_url)

        elif p_tag == 'title':
            self.rec = PARSE_TAGS.S_TITLE


        # ssrcss-15xko80-StyledHeading e1fj1fc10
        elif p_tag == 'h1' or p_tag == 'h2' or p_tag == 'h3' or p_tag == 'h4':
            self.rec = PARSE_TAGS.S_HEADER
            if p_tag == 'h1' and p_attrs[0][1] == "ssrcss-15xko80-StyledHeading e1fj1fc10":
                self.rec = PARSE_TAGS.S_ARTICLE_HEADER

        elif p_tag == 'span' and self.m_paragraph_count == 0:
            self.rec = PARSE_TAGS.S_SPAN

        elif p_tag == 'span' and self.rec == PARSE_TAGS.S_ARTICLE_AUTHOR:
            self.rec = PARSE_TAGS.S_ARTICLE_AUTHOR

        elif p_tag == 'strong' and self.rec == PARSE_TAGS.S_ARTICLE_AUTHOR:
            self.rec = PARSE_TAGS.S_ARTICLE_AUTHOR

        elif p_tag == 'div':
            self.rec = PARSE_TAGS.S_DIV

        elif p_tag == 'time':
            self.m_article_model.m_date = p_attrs[1][1]
            self.rec = PARSE_TAGS.S_ARTICLE_TIME

        elif p_tag == 'li':
            self.rec = PARSE_TAGS.S_PARAGRAPH

        elif p_tag == 'br':
            self.rec = PARSE_TAGS.S_BR

        elif p_tag == 'p':
            self.rec = PARSE_TAGS.S_PARAGRAPH
            self.m_paragraph_count += 1
            if len(p_attrs) > 0 and len(p_attrs[0]) > 1 and p_attrs[0][1] == "ssrcss-1q0x1qg-Paragraph eq5iqo00":
                self.rec = PARSE_TAGS.S_ARTICLE_PARAGRAPH
            if len(p_attrs) > 0 and len(p_attrs[0]) > 1 and p_attrs[0][1] == "ssrcss-ugte5s-Contributor e5xb54n2":
                self.rec = PARSE_TAGS.S_ARTICLE_AUTHOR
                return

        elif p_tag == 'meta':
            try:
                if p_attrs[0][0] == 'content':
                    if p_attrs[0][1] is not None and len(p_attrs[0][1]) > 50 and p_attrs[0][1].count(" ") > 4 and \
                            p_attrs[0][1] not in self.m_meta_content:
                        self.m_meta_content += p_attrs[0][1]
                if p_attrs[0][1] == 'description':
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][1] is not None:
                        self.m_meta_description += p_attrs[1][1]
                elif p_attrs[0][1] == 'keywords':
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][1] is not None:
                        self.m_meta_keyword = p_attrs[1][1].replace(",", " ")
            except Exception:
                pass
        else:
            self.rec = PARSE_TAGS.S_NONE

    def handle_endtag(self, p_tag):
        if p_tag == 'p':
            self.m_paragraph_count -= 1
        if self.rec != PARSE_TAGS.S_BR:
            self.rec = PARSE_TAGS.S_NONE

    def handle_data(self, p_data):
        if self.rec == PARSE_TAGS.S_HEADER:
            self.__add_important_description(p_data)
        if self.rec == PARSE_TAGS.S_ARTICLE_HEADER:
            self.__add_important_description(p_data)
            self.m_article_model.m_sub_header = p_data
        if self.rec == PARSE_TAGS.S_TITLE:
            self.m_article_model.m_title = p_data
        if self.rec == PARSE_TAGS.S_TITLE and len(self.m_title) == 0:
            self.m_title = p_data
            self.m_article_model.m_title = p_data
        elif self.rec == PARSE_TAGS.S_META and len(self.m_title) > 0:
            self.m_title = p_data
        elif self.rec == PARSE_TAGS.S_PARAGRAPH or self.rec == PARSE_TAGS.S_BR:
            self.__add_important_description(p_data)
        elif self.rec == PARSE_TAGS.S_ARTICLE_PARAGRAPH:
            self.__add_important_description(p_data)
            self.m_article_model.m_text += p_data
        elif self.rec == PARSE_TAGS.S_ARTICLE_AUTHOR:
            self.__add_important_description(p_data)
            self.m_article_model.m_authors = p_data
        elif self.rec == PARSE_TAGS.S_SPAN and p_data.count(' ') > 5:
            self.__add_important_description(p_data)
        elif self.rec == PARSE_TAGS.S_DIV:
            if p_data.count(' ') > 5 and p_data not in self.m_non_important_text:
                self.m_non_important_text += p_data
        elif self.rec == PARSE_TAGS.S_NONE:
            if self.m_paragraph_count > 0:
                self.__add_important_description(p_data)
        if self.rec == PARSE_TAGS.S_BR:
            self.rec = PARSE_TAGS.S_NONE

    # creating keyword request_manager1 for webpage representation
    def __add_important_description(self, p_data):
        p_data = " ".join(p_data.split())
        if (p_data.__contains__("java") and p_data.__contains__("script")) or p_data.__contains__("cookies"):
            return

        if (p_data.count(' ') > 2 or (self.m_paragraph_count > 0 and len(
                p_data) > 0 and p_data != " ")) and p_data not in self.m_important_content:
            if self.m_parsed_paragraph_count < 8:
                self.m_important_content_raw.append(p_data)
                self.m_parsed_paragraph_count += 1

                p_data = re.sub('[^A-Za-z0-9 ,;"\]\[/.+-;!\'@#$%^&*_+=]', '', p_data)
                p_data = re.sub(' +', ' ', p_data)
                p_data = re.sub(r'^\W*', '', p_data)

                if p_data.lower() in self.m_important_content.lower():
                    return
                self.m_important_content = self.m_important_content + " " + spell_checker_handler.get_instance().clean_paragraph(p_data.lower())

                if len(self.m_important_content) > 250:
                    self.m_parsed_paragraph_count = 9

                if len(self.m_important_content) > 550:
                    self.m_important_content = self.m_important_content[0:550]

    def __clean_text(self, p_text):
        m_text = p_text

        for m_important_content_item in self.m_important_content_raw:
            m_text = m_text.replace(m_important_content_item, ' ')

        m_text = m_text.replace('\n', ' ')
        m_text = m_text.replace('\t', ' ')
        m_text = m_text.replace('\r', ' ')
        m_text = m_text.replace(' ', ' ')

        m_text = re.sub(' +', ' ', m_text)

        # Lower Case
        p_text = m_text.lower()

        # Tokenizer
        m_word_tokenized = p_text.split()

        # Word Checking
        m_content = STRINGS.S_EMPTY
        for m_token in m_word_tokenized:
            if helper_method.is_stop_word(m_token) is False and m_token.isnumeric() is False:
                m_valid_status = spell_checker_handler.get_instance().validate_word(m_token)
                if m_valid_status is True:
                    m_content += " " + m_token
                else:
                    m_content += " " + spell_checker_handler.get_instance().clean_sentence(m_token)

        m_content = ' '.join(m_content.split())
        return m_content

    def __generate_html(self):
        m_soup = BeautifulSoup(self.m_html, "html.parser")
        self.m_content = self.__clean_text(m_soup.get_text())

    # ----------------- Data Recievers -----------------

    def __get_title(self):
        return helper_method.strip_special_character(self.m_title).strip()

    def __get_meta_description(self):
        return helper_method.strip_special_character(self.m_important_content)

    def __get_title_hidden(self, p_title_hidden):
        return self.__clean_text(p_title_hidden)

    def __get_meta_description_hidden(self, p_description_hidden):
        return self.__clean_text(p_description_hidden)

    def __get_important_content(self):
        m_content = self.m_important_content
        if len(m_content) < 150 and fuzz.ratio(m_content, self.m_meta_description) < 85 and len(
                self.m_meta_description) > 10:
            m_content += self.m_meta_description
        if len(m_content) < 150 and fuzz.ratio(m_content, self.m_non_important_text) < 85 and len(
                self.m_non_important_text) > 10:
            self.__add_important_description(self.m_non_important_text)
            m_content += self.m_important_content
        if len(m_content) < 50 and len(self.m_sub_url) >= 3:
            m_content = "- No description found but contains some urls. This website is most probably a search engine or only contain references of other websites - " + self.m_title.lower()

        return helper_method.strip_special_character(m_content)[0:300]

    def __get_validity_score(self, p_important_content):
        m_rank = (((len(p_important_content) + len(self.m_title)) > 150) or 5 >= 3) * 10 + (
                5 > 0 or self.all_url_count > 5) * 5
        return m_rank

    def __get_content_type(self):
        if len(self.m_content) > 0:
            self.m_content_type = topic_classifier_controller.get_instance().invoke_trigger(
                TOPIC_CLASSFIER_COMMANDS.S_PREDICT_CLASSIFIER, [self.m_title, self.m_important_content, self.m_content])
        return self.m_content_type

    def __get_static_file(self):
        return self.m_sub_url, self.m_image_url, self.m_doc_url, self.m_video_url

    def __get_content(self):
        return self.m_content

    def __get_meta_keywords(self):
        return self.m_meta_keyword

    def get_human_names(self, p_article):
        tokens = nltk.tokenize.word_tokenize(p_article)
        pos = nltk.pos_tag(tokens)
        sentt = nltk.ne_chunk(pos, binary=False)
        person_list = []
        person = []
        name = ""
        for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
            for leaf in subtree.leaves():
                person.append(leaf[0])
            if len(person) > 1:  # avoid grabbing lone surnames
                for part in person:
                    name += part + ' '
                if name[:-1] not in person_list:
                    person_list.append(name[:-1])
                name = ''
            person = []

        return person_list

    def __generate_url_topic(self):

        if self.m_base_url.startswith("https://www.bbc.com/news/"):
            self.m_article_model.m_webpage_topic = self.m_base_url[len("https://www.bbc.com/news/"):self.m_base_url.find('/', 26)]
            self.m_article_model.m_webpage_topic = re.sub('[^A-Za-z]+', ' ', self.m_article_model.m_webpage_topic).strip()

        if self.m_base_url.startswith("https://bbc.com/news/"):
            self.m_article_model.m_webpage_topic = self.m_base_url[len("https://bbc.com/news/"):self.m_base_url.find('/', 26)]
            self.m_article_model.m_webpage_topic = re.sub('[^A-Za-z]+', ' ', self.m_article_model.m_webpage_topic).strip()


    def __punctuation_removal(self, p_query):
        all_list = [char for char in p_query if char not in string.punctuation]
        clean_str = ''.join(all_list)
        return clean_str

    def __clean_fake_news(self, p_query):
        m_query = p_query
        m_query = m_query.lower()
        m_query = self.__punctuation_removal(m_query)
        m_query = [word for word in m_query.split(" ") if word not in stopwords.words('english')]
        m_query = " ".join(m_query)
        return m_query

    def __generate_article_analytics(self, p_validity_score, p_content_type, p_video, p_images):
        URL = "http://192.168.10.7:8000/fakenews/"
        PARAMS = {'article': self.__clean_fake_news(self.m_article_model.m_text)}
        response = requests.get(url=URL, params=PARAMS)
        response = response.text.replace("[", "").replace("]", "").split(" ")

        self.__generate_url_topic()
        self.m_article_model.id = helper_method.on_random_key(15)
        self.m_article_model.m_fake_news_score_negative = response[0]
        self.m_article_model.m_fake_news_score_positive = response[1]
        self.m_article_model.m_page_yield_score = p_validity_score
        self.m_article_model.m_content_time = str(datetime.date.today().strftime("%d/%m/%Y %H:%M:%S"))
        self.m_article_model.m_offiensive_images = False
        self.m_article_model.m_learned_topic = False
        self.m_article_model.m_learned_topic = p_content_type
        self.m_article_model.m_documents.extend(self.m_doc_url)
        self.m_article_model.m_internal_redirection.extend(self.m_sub_url)
        self.m_article_model.m_video.extend(p_video)
        self.m_article_model.m_images_references.extend(p_images)
        self.m_article_model.m_emails = re.findall(r'[\w\.-]+@[\w\.-]+', self.m_article_model.m_text)
        self.m_article_model.m_names.extend(self.get_human_names(self.m_article_model.m_text))
        self.m_article_model.url = self.m_base_url

    def parse_html_files(self):
        self.__generate_html()

        m_sub_url, m_images, m_document, m_video = self.__get_static_file()
        m_title = self.__get_title()
        m_meta_description = self.__get_meta_description()
        m_title_hidden = STRINGS.S_EMPTY
        m_important_content = self.__get_important_content()
        m_meta_keywords = self.__get_meta_keywords()
        m_content_type = self.__get_content_type()
        m_content = self.__get_content() + " " + m_title + " " + m_meta_description
        m_validity_score = self.__get_validity_score(m_important_content)
        m_important_content_hidden = self.__get_meta_description_hidden(self.m_meta_content + " " + m_title + " " + m_meta_description + " " + m_important_content)

        if self.m_depth != 0:
            self.__generate_article_analytics(m_validity_score, m_content_type, m_video, m_images)
        else:
            self.m_article_model = None

        return m_title, self.m_meta_content + m_meta_description, m_title_hidden, m_important_content, m_important_content_hidden, m_meta_keywords, m_content, m_content_type, m_sub_url, m_images, m_document, m_video, m_validity_score, self.m_article_model
