import json


class Error(Exception):
    def __init__(self, msg):
        self.msg = msg

    def to_response(self):
        return json.dumps({
            'type': 'error',
            'message': self.msg
        })


class InternalError(Error):
    def __init__(self, logger, internal_message):
        super().__init__("internal error")
        logger.error(internal_message)


def check_requested_updates(requested_updates):
    if not isinstance(requested_updates, int):
        raise Error("'requested_updates' needs to be a number")

    if requested_updates <= 0:
        raise Error("'requested_updates' needs to be > 0")

