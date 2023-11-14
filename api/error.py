import json


def error(msg):
    return json.dumps({
        'type': 'error',
        'message': msg
    })


def check_valid_search_request(client, req):
    if "requested_updates" in req:  # check if key exists
        if not (req.get('preferred_radios') is None):  # check if value for key exists
            if isinstance(req["preferred_radios"], int):  # check if value is an int
                if req["preferred_radios"] > 0:
                    pass
                else:
                    client.send(error('search_request/requested_updates: Value is < 0'))
                    return False
            else:
                client.send(error('search_request/requested_updates: Value is not an int'))
                return False
        else:
            client.send(error('search_request/requested_updates: No Value'))
            return False
    else:
        client.send(error('search_request: No key requested_updates'))
        return False

    if "query" in req:
        if not (req.get('query') is None):
            if isinstance(req["query"], str):
                if req["query"] != "":
                    pass
                else:
                    client.send(error('search_request/query: invalid Value ""'))
                    return False
            else:
                client.send(error('search_request/query: Value is not a str'))
                return False
        else:
            client.send(error('search_request/query: No Value'))
            return False
    else:
        client.send(error('search_request: No key query'))
        return False

    if "filter" in req:
        if not (req.get('filter') is None):
            if isinstance(req["filter"], dict):
                if req["filter"]:
                    if "ids" in req["filter"] and "without_ads" in req["filter"]:
                        if req["filter"].get('ids') and req["filter"].get('without_ads'):
                            if isinstance(req["filter"]["ids"], list):
                                if all(isinstance(s, int) for s in req["filter"]["ids"]):
                                    if all(0 < i < 7 for i in req["radios"]["all"]):
                                        pass
                                    else:
                                        client.send(error('search_request/filter/ids: Some/all Values is list are not '
                                                          'valid indexes'))
                                        return False
                                else:
                                    client.send(error('search_request/filter/ids: Some/all Values in list are not int'))
                                    return False
                            else:
                                client.send(error('search_request/filter/ids: Values is not a list'))
                                return False
                            if isinstance(req["filter"]["without_ads"], bool):
                                pass
                            else:
                                client.send(error('search_request/filter/without_ads: Values is not a bool'))
                                return False
                        else:
                            client.send(error('search_request/filter/ids.without_ads: No Values'))
                            return False
                    else:
                        client.send(error('search_request/filter/ids.without_ads: No keys ids / without_ads'))
                        return False
                else:
                    client.send(error('search_request/filter: dict is empty'))
                    return False
            else:
                client.send(error('search_request/filter: Value is not a dict'))
                return False
        else:
            client.send(error('search_request/filter: No Value'))
            return False
    else:
        client.send(error('search_request: No key filter'))
        return False
    return True


def check_valid_search_update_request(client, req):
    if "requested_updates" in req:
        if not (req.get('requested_updates') is None):
            if isinstance(req["requested_updates"], int):
                if req["requested_updates"] > 0:
                    pass
                else:
                    client.send(error('search_update_request: value for key requested_updates is < 1'))
                    return False
        else:
            client.send(error('search_update_request: value for key requested_updates does not exist'))
            return False
    else:
        client.send(error('search_update_request: key requested_updates does not exist'))
        return False
    return True


def check_valid_stream_request(client, req):
    if "preferred_radios" in req:  # check if key exists
        if not (req.get('preferred_radios') is None):  # check if value for key exists
            if isinstance(req["preferred_radios"], list):  # check if value is a list
                if req["preferred_radios"]:  # check if list is empty
                    if all(isinstance(s, int) for s in req["preferred_radios"]):  # check if list-elements are int
                        if all(0 < i < 7 for i in req["preferred_radios"]):  # check if list-elements are valid indexes
                            pass
                        else:
                            client.send(error('stream_request: Invalid indexes in preferred_radios'))
                            return False
                    else:
                        client.send(error('stream_request: All/Some elements of preferred_radios aren´t strings'))
                        return False
                else:
                    client.send(error('stream_request: preferred_radios List is empty'))
                    return False
            else:
                client.send(error('stream_request: preferred_radios is not a list'))
                return False
        else:
            client.send(error('stream_request: Missing Value for preferred_radios'))
            return False
    else:
        client.send(error('stream_request: Missing Key preferred_radios'))
        return False

    if "preferred_genres" in req:
        if not (req.get('preferred_genres') is None):
            if isinstance(req["preferred_genres"], list):
                if req["preferred_genres"]:
                    if all(isinstance(s, int) for s in req["preferred_genres"]):
                        if all(0 < i < 7 for i in req["preferred_genres"]):
                            pass
                        else:
                            client.send(error('stream_request: Invalid indexes in preferred_genres'))
                            return False
                    else:
                        client.send(error('stream_request: All/Some elements of preferred_genres aren´t strings'))
                        return False
                else:
                    client.send(error('stream_request: preferred_genres List is empty'))
                    return False
            else:
                client.send(error('stream_request: preferred_genres is not a list'))
                return False
        else:
            client.send(error('stream_request: Missing Value for preferred_genres'))
            return False
    else:
        client.send(error('stream_request: Missing Key preferred_genres'))
        return False

    if "preferred_experience" in req:
        if not (req.get('preferred_experience') is None):
            if isinstance(req["preferred_experience"], dict):
                if req["preferred_experience"]:
                    if "ad" in req["preferred_experience"] and "talk" in req["preferred_experience"] and "news" in req[
                        "preferred_experience"] and "music" in req["preferred_experience"]:
                        if req["preferred_experience"].get('ad') and req["preferred_experience"].get('talk') and req[
                            "preferred_experience"].get('news') and req["preferred_experience"].get('music'):
                            if all(isinstance(s, bool) for s in req["preferred_experience"]):
                                pass
                            else:
                                client.send(error('stream_request/preferred_experience: All/Some values in dict are '
                                                  'not bool'))
                                return False
                        else:
                            client.send(error('stream_request/preferred_experience: missing values in dict'))
                            return False
                    else:
                        client.send(error('stream_request/preferred_experience: missing keys in dict'))
                        return False
                else:
                    client.send(error('stream_request: preferred_experience dict is empty'))
                    return False
            else:
                client.send(error('stream_request: preferred_experience is not a dict'))
                return False
        else:
            client.send(error('stream_request: Missing Value for preferred_experience'))
            return False
    else:
        client.send(error('stream_request: Missing Key preferred_experience'))
        return False
    return True
