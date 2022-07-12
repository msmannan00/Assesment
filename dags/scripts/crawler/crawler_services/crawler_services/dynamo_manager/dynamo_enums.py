import enum


class DYNAMO_COMMANDS(enum.Enum):
    S_INSERT_ARTICLE = 1
    S_GET_ALL_ARTICLE = 2
    S_DELETE_ARTICLES_BY_ID = 3


class DYNAMO_COLLECTIONS:
    S_MONGO_INDEX_MODEL = 'analytics_model'


class DYNAMO_CONNECTIONS:
    S_DATABASE_NAME = 'genbot-crawler'
    S_DATABASE_PORT = 8000
    S_DATABASE_IP = '10.0.0.104'


class DYNAMO_CRUD(enum.Enum):
    S_CREATE = '1'
    S_READ = '2'
    S_UPDATE = '3'
    S_DELETE = '4'


class DYNAMO_KEYS:
    S_DOCUMENT = 'm_document'
    S_FILTER = 'm_filter'
    S_VALUE = 'm_value'


class DYNAMO_PROPERTIES:
    S_SORT = 'm_sort'
