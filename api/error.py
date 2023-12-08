import json

from api.db.database_functions import radios_existing


class Error(Exception):
    def __init__(self, msg):
        self.msg = msg

    def to_response(self):
        return json.dumps({
            'type': 'error',
            'message': self.msg
        })


class InternalError(Error):
    def __init__(self):
        super().__init__("internal error")


def check_requested_updates(requested_updates):
    if not isinstance(requested_updates, int):
        raise Error("'requested_updates' needs to be a number")

    if requested_updates <= 0:
        raise Error("'requested_updates' needs to be > 0")


def get_or_raise(kv, key):
    if key not in kv:
        raise Error(f"you need to specify key '{key}'")
    return kv[key]


def check_valid_stream_request(req):
    preferred_radios = get_or_raise(req, "preferred_radios")
    if preferred_radios is None:
        raise Error("'preferred_radios' can't be null")

    if not isinstance(preferred_radios, list):  # check if value is a list
        raise Error("'preferred_radios' must be a list")

    if len(preferred_radios) > 0:  # check if list is empty
        if not all(isinstance(s, int) for s in preferred_radios):  # check if list-elements are int
            raise Error("every entry in 'preferred_radios' must be an id (integer number)")

        if len(set(preferred_radios)) != len(preferred_radios):
            raise Error("'preferred_radios' mustn't have duplicate ids")

        if not radios_existing(preferred_radios):
            raise Error("Atleast one id doesn't exist in the database")

    preferred_experience = get_or_raise(req, "preferred_experience")

    if preferred_experience is None:
        raise Error("'preferred_experience' can't be null")
    if not isinstance(preferred_experience, dict):
        raise Error("'preferred_experience' needs to be of type { ... }")
    if not all((key in preferred_experience for key in ['talk', 'music', 'ad', 'news'])):
        raise Error("'preferred_experience' needs to have keys 'talk', 'music', 'ad' and 'news'")
    if not all((isinstance(preferred_experience[key], bool) for key in ['talk', 'music', 'ad', 'news'])):
        raise Error("keys of 'preferred_experience' need to be of type boolean")
