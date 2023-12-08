import json
import logging
from logs.logging_config import configure_logging
configure_logging()

logger = logging.getLogger("ErrorTest.py")


def error(msg):
    return json.dumps({
        'type': 'error',
        'message': msg
    })


def check_valid_stream_request(req):
    if "preferred_radios" in req:  # check if key exists
        if not (req.get('preferred_radios') is None):  # check if value for key exists
            if isinstance(req["preferred_radios"], list):  # check if value is a list
                if req["preferred_radios"]:  # check if list is empty
                    if all(isinstance(s, int) for s in req["preferred_radios"]):  # check if list-elements are int
                        if all(0 < i < 7 for i in req["preferred_radios"]):  # check if list-elements are valid indexes
                            pass
                        else:
                            logger.error(error('stream_request: Invalid indexes in preferred_radios'))
                            return False
                    else:
                        logger.error(error('stream_request: All/Some elements of preferred_radios aren´t strings'))
                        return False
                else:
                    logger.error(error('stream_request: preferred_radios List is empty'))
                    return False
            else:
                logger.error(error('stream_request: preferred_radios is not a list'))
                return False
        else:
            logger.error(error('stream_request: Missing Value for preferred_radios'))
            return False
    else:
        logger.error(error('stream_request: Missing Key preferred_radios'))
        return False

    if "preferred_genres" in req:
        if not (req.get('preferred_genres') is None):
            if isinstance(req["preferred_genres"], list):
                if req["preferred_genres"]:
                    if all(isinstance(s, int) for s in req["preferred_genres"]):
                        if all(0 < i < 7 for i in req["preferred_genres"]):
                            pass
                        else:
                            logger.error(error('stream_request: Invalid indexes in preferred_genres'))
                            return False
                    else:
                        logger.error(error('stream_request: All/Some elements of preferred_genres aren´t strings'))
                        return False
                else:
                    logger.error(error('stream_request: preferred_genres List is empty'))
                    return False
            else:
                logger.error(error('stream_request: preferred_genres is not a list'))
                return False
        else:
            logger.error(error('stream_request: Missing Value for preferred_genres'))
            return False
    else:
        logger.error(error('stream_request: Missing Key preferred_genres'))
        return False

    if "preferred_experience" in req:
        if not (req.get('preferred_experience') is None):
            if isinstance(req["preferred_experience"], dict):
                if req["preferred_experience"]:
                    if "ad" in req["preferred_experience"] and "talk" in req["preferred_experience"] and "news" in req[
                        "preferred_experience"] and "music" in req["preferred_experience"]:
                        if req["preferred_experience"].get("ad") != None and req["preferred_experience"].get(
                                "talk") != None and req["preferred_experience"].get("news") != None and req[
                            "preferred_experience"].get("music") != None:
                            if all(isinstance(s, bool) for s in req["preferred_experience"].values()):
                                pass
                            else:
                                logger.error(error('stream_request/preferred_experience: All/Some values in dict are '
                                            'not bool'))
                                return False
                        else:
                            logger.error(error('stream_request/preferred_experience: missing values in dict'))
                            return False
                    else:
                        logger.error(error('stream_request/preferred_experience: missing keys in dict'))
                        return False
                else:
                    logger.error(error('stream_request: preferred_experience dict is empty'))
                    return False
            else:
                logger.error(error('stream_request: preferred_experience is not a dict'))
                return False
        else:
            logger.error(error('stream_request: Missing Value for preferred_experience'))
            return False
    else:
        logger.error(error('stream_request: Missing Key preferred_experience'))
        return False
    return True


def check_valid_search_update_request(req):
    if "requested_updates" in req:
        if not (req.get('requested_updates') is None):
            if isinstance(req["requested_updates"], int):
                if req["requested_updates"] > 0:
                    pass
                else:
                    logger.error(error('search_update_request: value for key requested_updates is < 1'))
                    return False
            else:
                logger.error(error('search_update_request: value for key requested_updates is not an int'))
                return False
        else:
            logger.error(error('search_update_request: value for key requested_updates does not exist'))
            return False
    else:
        logger.error(error('search_update_request: key requested_updates does not exist'))
        return False
    return True


def check_valid_search_request(req):
    if "requested_updates" in req:  # check if key exists
        if not (req.get('requested_updates') is None):  # check if value for key exists
            if isinstance(req["requested_updates"], int):  # check if value is an int
                if req["requested_updates"] > 0:
                    pass
                else:
                    logger.error(error('search_request/requested_updates: Value is < 0'))
                    return False
            else:
                logger.error(error('search_request/requested_updates: Value is not an int'))
                return False
        else:
            logger.error(error('search_request/requested_updates: No Value'))
            return False
    else:
        logger.error(error('search_request: No key requested_updates'))
        return False

    if "query" in req:
        if not (req.get('query') is None):
            if isinstance(req["query"], str):
                if req["query"] != "":
                    pass
                else:
                    logger.error(error('search_request/query: invalid Value for query'))
                    return False
            else:
                logger.error(error('search_request/query: Value is not a str'))
                return False
        else:
            logger.error(error('search_request/query: No Value'))
            return False
    else:
        logger.error(error('search_request: No key query'))
        return False

    if "filter" in req:
        if not (req.get('filter') is None):
            if isinstance(req["filter"], dict):
                if req["filter"]:
                    if "ids" in req["filter"] and "without_ads" in req["filter"]:
                        if req["filter"].get('ids') != None and req["filter"].get('without_ads') != None:
                            if isinstance(req["filter"]["ids"], list):
                                if req["filter"]["ids"]:
                                    if all(isinstance(s, int) for s in req["filter"]["ids"]):
                                        if all(0 < i < 7 for i in req["filter"]["ids"]):
                                            pass
                                        else:
                                            logger.error(error('search_request/filter/ids: Some/all Values is list are not '
                                                        'valid indexes'))
                                            return False
                                    else:
                                        logger.error(error('search_request/filter/ids: Some/all Values in list are not int'))
                                        return False
                                else:
                                    logger.error(error('search_request/filter/ids: list is empty'))
                                    return False
                            else:
                                logger.error(error('search_request/filter/ids: Values is not a list'))
                                return False
                            if isinstance(req["filter"]["without_ads"], bool):
                                pass
                            else:
                                logger.error(error('search_request/filter/without_ads: Values is not a bool'))
                                return False
                        else:
                            logger.error(error('search_request/filter/ids.without_ads: No Values'))
                            return False
                    else:
                        logger.error(error('search_request/filter/ids.without_ads: No keys ids / without_ads'))
                        return False
                else:
                    logger.error(error('search_request/filter: dict is empty'))
                    return False
            else:
                logger.error(error('search_request/filter: Value is not a dict'))
                return False
        else:
            logger.error(error('search_request/filter: No Value'))
            return False
    else:
        logger.error(error('search_request: No key filter'))
        return False
    return True


def search_request(query, requested_updates):
    return (json.dumps({
        'type': 'search_request',
        'query': query,
        'requested_updates': requested_updates,
        'filter': {
            'ids': [],
            'without_ads': False
        }
    }))


def search_update_request(requested_updates=1):
    return (json.dumps({
        'type': 'search_update_request',
        'requested_updates': requested_updates
    }))


def stream_request():
    return (json.dumps({
        'type': 'stream_request',
        'preferred_radios': [1],
        'preferred_genres': [1],
        'preferred_experience': {'ad': True, 'news': True, 'music': True, 'talk': False}

    }))


def play():
    data = json.loads(search_request("1", 1))
    logger.error(check_valid_search_request(data))


if __name__ == '__main__':
    play()
