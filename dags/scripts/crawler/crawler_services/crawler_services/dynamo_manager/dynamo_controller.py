# Local Imports
import boto3
from scripts.crawler.constants.strings import MANAGE_DATABASE_MESSAGES
from scripts.crawler.crawler_services.crawler_services.dynamo_manager.dynamo_enums import DYNAMO_KEYS, DYNAMO_CRUD, DYNAMO_CONNECTIONS, DYNAMO_COLLECTIONS
from scripts.crawler.crawler_services.crawler_services.dynamo_manager.dynamo_request_generator import dynamo_request_generator
from scripts.crawler.crawler_shared_directory.log_manager.log_controller import log
from scripts.crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class dynamo_controller(request_handler):
    __instance = None
    __m_connection = None
    __m_dynamo_request_generator = None

    # Initializations
    @staticmethod
    def get_instance():
        if dynamo_controller.__instance is None:
            dynamo_controller()
        return dynamo_controller.__instance

    def __init__(self):
        dynamo_controller.__instance = self
        self.__m_dynamo_request_generator = dynamo_request_generator()
        self.link_connection()
        # self.__reset()

    def __reset(self):
        table = self.__m_connection.Table(DYNAMO_COLLECTIONS.S_MONGO_INDEX_MODEL)
        tableKeyNames = [key.get("AttributeName") for key in table.key_schema]
        projectionExpression = ", ".join('#' + key for key in tableKeyNames)
        expressionAttrNames = {'#' + key: key for key in tableKeyNames}
        counter = 0
        page = table.scan(ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames)
        with table.batch_writer() as batch:
            while page["Count"] > 0:
                counter += page["Count"]
                for itemKeys in page["Items"]:
                    batch.delete_item(Key=itemKeys)
                if 'LastEvaluatedKey' in page:
                    page = table.scan(
                        ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames,
                        ExclusiveStartKey=page['LastEvaluatedKey'])
                else:
                    break
        print(f"Deleted {counter}")

    def initialize(self):
        try:
            self.__m_connection.create_table(
                TableName=DYNAMO_COLLECTIONS.S_MONGO_INDEX_MODEL,

                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1,
                }
            )
        except Exception:
            pass

    def link_connection(self):
        self.__m_connection = boto3.resource("dynamodb", endpoint_url='http://' + DYNAMO_CONNECTIONS.S_DATABASE_IP + ':' + str(DYNAMO_CONNECTIONS.S_DATABASE_PORT), region_name='dummy', aws_access_key_id='dummy', aws_secret_access_key='dummy')
        self.initialize()

    def __create(self, p_data):
        try:

            m_collection = self.__m_connection.Table(p_data[DYNAMO_KEYS.S_DOCUMENT])
            m_collection.put_item(Item=p_data[DYNAMO_KEYS.S_VALUE])
            return True, MANAGE_DATABASE_MESSAGES.S_INSERT_SUCCESS
        except Exception as ex:
            log.g().e(MANAGE_DATABASE_MESSAGES.S_INSERT_FAILURE + " : " + str(ex))
            return False, str(ex)

    def __read(self, p_data):
        try:
            m_collection = self.__m_connection.Table(p_data[DYNAMO_KEYS.S_DOCUMENT])
            if DYNAMO_KEYS.S_FILTER not in p_data:
                response = m_collection.scan()
                return True, response['Items']
            else:
                return False, None
        except Exception as ex:
            log.g().e(MANAGE_DATABASE_MESSAGES.S_READ_FAILURE + " : " + str(ex))
            return False, str(ex)

    def __update(self):
        try:
            return True, "not implemented"
        except Exception as ex:
            log.g().e(MANAGE_DATABASE_MESSAGES.S_UPDATE_FAILURE + " : " + str(ex))
            return False, str(ex)

    def __delete(self, p_data):
        try:
            m_collection = self.__m_connection.Table(p_data[DYNAMO_KEYS.S_DOCUMENT])
            m_collection.delete_item(Key=p_data[DYNAMO_KEYS.S_FILTER], ConditionExpression="attribute_exists(id)")
            return True, MANAGE_DATABASE_MESSAGES.S_DELETE_SUCCESS
        except Exception as ex:
            log.g().e(MANAGE_DATABASE_MESSAGES.S_DELETE_FAILURE + " : " + str(ex))
            return False, str(ex)

    def invoke_trigger(self, p_commands, p_data=None):

        m_request = p_data[0]
        m_data = p_data[1]
        m_param = p_data[2]
        m_request = self.__m_dynamo_request_generator.invoke_trigger(m_request, m_data)

        if p_commands == DYNAMO_CRUD.S_CREATE:
            return self.__create(m_request)
        elif p_commands == DYNAMO_CRUD.S_READ:
            return self.__read(m_request)
        elif p_commands == DYNAMO_CRUD.S_UPDATE:
            return self.__update()
        elif p_commands == DYNAMO_CRUD.S_DELETE:
            return self.__delete(m_request)
