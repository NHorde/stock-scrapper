from bs4 import BeautifulSoup
import requests
import re
import json
from json import loads

from libs.state import State
from libs.logger import BASE_LOGGER

LOGGER = BASE_LOGGER.getChild(__name__)

def get_html(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    soup = BeautifulSoup(requests.get("https://finance.yahoo.com/quote/%s/key-statistics?p=%s" % ("AMZN", "AMZN")).content, "lxml")
    script = soup.find("script", text=re.compile("root.App.main")).text
    data = loads(re.search("root.App.main\s+=\s+(\{.*\})", script).group(1))
    state.url = data['context']['dispatcher']['stores']

    LOGGER.info("Successfully get URL for ticker")

    return crawler_quote_summary(state=state)


def crawler_quote_summary(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.quote_summary_store = state.url['QuoteSummaryStore']
        LOGGER.info('Successfully retrieving QuoteSummaryStore list')
    except ValueError:
        state.quote_summary_store = None
    return crawler_financial_data(state=state)


def crawler_financial_data(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.financial_data = state.quote_summary_store['financialData']
        LOGGER.info("Successfully retrieving financialData")
    except ValueError:
        state.financial_data = None
    return get_current_price(state=state)


def get_current_price(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.current_price = state.financial_data['currentPrice']['fmt']
        LOGGER.info("Current company price scrapped")
    except ValueError:
        state.current_price = None
    return crawler_default_key_statistics(state=state)


def crawler_default_key_statistics(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.default_key_statistics = state.quote_summary_store['defaultKeyStatistics']

    except ValueError:
        state.default_key_statistics = None
    return get_price_to_book(state=state)


def get_price_to_book(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.price_to_book = state.default_key_statistics['priceToBook']['fmt']
    except ValueError:
        state.price_to_book = None
    return status(state=state)


def status(state: State):
    """
    :param state: object
    :type state: class
    :rtype: dict
    :return: state
    """
    state.status = 100
    return state


def manager(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        result = get_html(state)
    except:
        result = state
    return result
