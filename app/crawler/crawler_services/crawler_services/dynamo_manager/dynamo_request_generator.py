from crawler.crawler_instance.local_shared_model.article_model import article_model
from crawler.crawler_services.crawler_services.dynamo_manager.dynamo_enums import DYNAMO_COMMANDS, DYNAMO_KEYS, \
    DYNAMO_COLLECTIONS
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class dynamo_request_generator(request_handler):

    def __init__(self):
        pass

    def on_insert_article(self, model: article_model):
        return {DYNAMO_KEYS.S_DOCUMENT: DYNAMO_COLLECTIONS.S_MONGO_INDEX_MODEL,
                DYNAMO_KEYS.S_VALUE: model.dict()}

    def on_fetch_article(self):
        return {DYNAMO_KEYS.S_DOCUMENT: DYNAMO_COLLECTIONS.S_MONGO_INDEX_MODEL}

    def on_delete_article_by_id(self, p_id):
        return {DYNAMO_KEYS.S_DOCUMENT: DYNAMO_COLLECTIONS.S_MONGO_INDEX_MODEL,
                DYNAMO_KEYS.S_FILTER: {"id": p_id}}

    def invoke_trigger(self, p_commands, p_data=None):
        if p_commands == DYNAMO_COMMANDS.S_INSERT_ARTICLE:
            return self.on_insert_article(p_data[0])
        if p_commands == DYNAMO_COMMANDS.S_GET_ALL_ARTICLE:
            return self.on_fetch_article()
        if p_commands == DYNAMO_COMMANDS.S_DELETE_ARTICLES_BY_ID:
            return self.on_delete_article_by_id(p_data[0])
