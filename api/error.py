import json


def error(msg):
    return json.dumps({
        'type': 'error',
        'message': msg
    })


def check_valid_stream_request(req, client):
    if not "preferred_radios" in req:  # check if key exists
        client.send(error('stream_request: Missing Key preferred_radios'))
        return False
    else:
        if (req.get('preferred_radios') is None):  # check if value for key exists
            client.send(error('stream_request: Missing Value for preferred_radios'))
            return False
        else:
            if not isinstance(req["preferred_radios"], list):  # check if value is a list
                client.send(error('stream_request: preferred_radios is not a list'))
                return False
            else:
                if not req["preferred_radios"]:  # check if list is empty
                    client.send(error('stream_request: preferred_radios List is empty'))
                    return False
                else:
                    if not all(isinstance(s, int) for s in req["preferred_radios"]):  # check if list-elements are int
                        client.send(error('stream_request: All/Some elements of preferred_radios aren´t int'))
                        return False
                    else:
                        if not all(
                                0 < i < 7 for i in req["preferred_radios"]):  # check if list-elements are valid indexes
                            client.send(error('stream_request: Invalid indexes in preferred_radios'))
                            return False

    if not "preferred_genres" in req:
        client.send(error('stream_request: Missing Key preferred_genres'))
        return False
    else:
        if (req.get('preferred_genres') is None):
            client.send(error('stream_request: Missing Value for preferred_genres'))
            return False
        else:
            if not isinstance(req["preferred_genres"], list):
                client.send(error('stream_request: preferred_genres is not a list'))
                return False
            else:
                if not req["preferred_genres"]:
                    client.send(error('stream_request: preferred_genres List is empty'))
                    return False
                else:
                    if not all(isinstance(s, int) for s in req["preferred_genres"]):
                        client.send(error('stream_request: All/Some elements of preferred_genres aren´t strings'))
                        return False
                    else:
                        if not all(0 < i < 7 for i in req["preferred_genres"]):
                            client.send(error('stream_request: Invalid indexes in preferred_genres'))
                            return False


    if not "preferred_experience" in req:
        client.send(error('stream_request: Missing Key preferred_experience'))
        return False
    else:
        if (req.get('preferred_experience') is None):
            client.send(error('stream_request: Missing Value for preferred_experience'))
            return False
        else:
            if not isinstance(req["preferred_experience"], dict):
                client.send(error('stream_request: preferred_experience is not a dict'))
                return False
            else:
                if not req["preferred_experience"]:
                    client.send(error('stream_request: preferred_experience dict is empty'))
                    return False
                else:
                    if not ("ad" in req["preferred_experience"] and "talk" in req["preferred_experience"] and "news" in req["preferred_experience"] and "music" in req["preferred_experience"]):
                        client.send(error('stream_request/preferred_experience: missing keys in dict'))
                        return False
                    else:
                        if not (req["preferred_experience"].get("ad") != None and req["preferred_experience"].get("talk") != None and req["preferred_experience"].get("news") != None and req["preferred_experience"].get("music") != None):
                            client.send(error('stream_request/preferred_experience: missing values in dict'))
                            return False
                        else:
                            if not all(isinstance(s, bool) for s in req["preferred_experience"].values()):
                                client.send(
                                    error('stream_request/preferred_experience: All/Some values in dict are not bool'))
                                return False
    return True


def check_valid_search_update_request(req, client):
    if not "requested_updates" in req:
        client.send(error('search_update_request: key requested_updates does not exist'))
        return False
    else:
        if req.get('requested_updates') is None:
            client.send(error('search_update_request: value for key requested_updates does not exist'))
            return False
        else:
            if not isinstance(req["requested_updates"], int):
                client.send(error('search_update_request: value for key requested_updates is not an int'))
                return False
            else:
                if not req["requested_updates"] > 0:
                    client.send(error('search_update_request: value for key requested_updates is < 1'))
                    return False
    return True


def check_valid_search_request(req, client):
    if not "requested_updates" in req:  # check if key exists
        client.send(error('search_request: No key requested_updates'))
        return False
    else:
        if req.get('requested_updates') is None:  # check if value for key exists
            client.send(error('search_request/requested_updates: No Value'))
            return False
        else:
            if not isinstance(req["requested_updates"], int):  # check if value is an int
                client.send(error('search_request/requested_updates: Value is not an int'))
                return False
            else:
                if not req["requested_updates"] > 0:
                    client.send(error('search_request/requested_updates: Value is < 0'))
                    return False

    if not "query" in req:
        client.send(error('search_request: No key query'))
        return False
    else:
        if req.get('query') is None:
            client.send(error('search_request/query: No Value'))
            return False
        else:
            if not isinstance(req["query"], str):
                client.send(error('search_request/query: Value is not a str'))
                return False
            else:
                if not req["query"] != "":
                    client.send(error('search_request/query: invalid Value for query'))
                    return False


    if not "filter" in req:
        client.send(error('search_request: No key filter'))
        return False
    else:
        if req.get('filter') is None:
            client.send(error('search_request/filter: No Value'))
            return False
        else:
            if not isinstance(req["filter"], dict):
                client.send(error('search_request/filter: Value is not a dict'))
                return False
            else:
                if not req["filter"]:
                    client.send(error('search_request/filter: dict is empty'))
                    return False
                else:
                    if not("ids" in req["filter"] and "without_ads" in req["filter"]):
                        client.send(error('search_request/filter/ids.without_ads: No keys ids / without_ads'))
                        return False
                    else:
                        if not(req["filter"].get('ids') != None and req["filter"].get('without_ads') != None):
                            client.send(error('search_request/filter/ids.without_ads: No Values'))
                            return False
                        else:
                            if not isinstance(req["filter"]["ids"], list):
                                client.send(error('search_request/filter/ids: Values is not a list'))
                                return False
                            else:
                                if not req["filter"]["ids"]:
                                    client.send(error('search_request/filter/ids: list is empty'))
                                    return False
                                else:
                                    if not all(isinstance(s, int) for s in req["filter"]["ids"]):
                                        client.send(error('search_request/filter/ids: Some/all Values in list are not int'))
                                        return False
                                    else:
                                        if not all(0 < i < 7 for i in req["filter"]["ids"]):
                                            client.send(error('search_request/filter/ids: Some/all Values is list are not ''valid indexes'))
                                            return False
                            if not isinstance(req["filter"]["without_ads"], bool):
                                client.send(error('search_request/filter/without_ads: Values is not a bool'))
                                return False
    return True


