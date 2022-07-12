from scripts.crawler.crawler_instance.application_controller.application_controller import application_controller
from scripts.crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS


def onInitializeWebsites():
    application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_INIT_APPLICATION_DOCKERISED)


def onCrawlWebsites():
    application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_START_APPLICATION_DOCKERISED)


def onAnalyticsWeekly():
    application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_LOAD_ANALYTICS_WEEKLY)


def onAnalyticsHourly():
    application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_LOAD_ANALYTICS)
