# Non Parsed URL Model
from pydantic import BaseModel
from scripts.crawler.constants.strings import STRINGS


class article_model(BaseModel):
    id: str = STRINGS.S_EMPTY
    url: str = STRINGS.S_EMPTY
    m_text: str = STRINGS.S_EMPTY
    m_title: str = STRINGS.S_EMPTY
    m_sub_header: str = STRINGS.S_EMPTY
    m_date: str = STRINGS.S_EMPTY
    m_authors: str = STRINGS.S_EMPTY
    m_fake_news_score_positive: str = STRINGS.S_EMPTY
    m_fake_news_score_negative: str = STRINGS.S_EMPTY
    m_page_yield_score: str = STRINGS.S_EMPTY
    m_content_time: str = STRINGS.S_EMPTY
    m_learned_topic: str = STRINGS.S_EMPTY
    m_webpage_topic: str = STRINGS.S_EMPTY
    m_offiensive_images: str = STRINGS.S_EMPTY

    m_documents: list = []
    m_internal_redirection: list = []
    m_external_redirection: list = []
    m_video: list = []
    m_images_priority: list = []
    m_images_references: list = []
    m_names: list = []
    m_emails: list = []
