from dotenv import load_dotenv
from os import getenv

from humanfriendly import parse_timespan, parse_size

load_dotenv()


def get_env(key):
    value = getenv(key)
    if value is None:
        raise Exception(f"You need to specify the environment variable '{key}'")
    return value


def env_str(key):
    return str(get_env(key))


def env_int(key):
    return int(get_env(key))


def env_timespan(key):
    # humandfriendly.parse_timestamp can't operate on composed time spans like '5h 40min' so let's fix that
    value = get_env(key)
    spans = value.strip().split(' ')
    return sum(int(parse_timespan(span)) for span in spans)

def env_size(key):
    return parse_size(get_env(key))


FINGERPRINT_MYSQL_HOST = env_str('FINGERPRINT_MYSQL_HOST')
FINGERPRINT_MYSQL_USER = env_str('FINGERPRINT_MYSQL_USER')
FINGERPRINT_MYSQL_PASSWORD = env_str('FINGERPRINT_MYSQL_PASSWORD')
FINGERPRINT_MYSQL_DB = env_str('FINGERPRINT_MYSQL_DB')

FINGERPRINT_WORKER_THREAD_COUNT = env_int('FINGERPRINT_WORKER_THREAD_COUNT')
CONFIDENCE_THRESHOLD = env_int('FINGERPRINT_CONFIDENCE_THRESHOLD')
PIECE_OVERLAP = env_timespan('FINGERPRINT_PIECE_OVERLAP')
PIECE_DURATION = env_timespan('FINGERPRINT_PIECE_DURATION')

STREAM_TIMEOUT = env_timespan('STREAM_TIMEOUT')
STREAM_AUTO_RESTART = env_timespan('STREAM_AUTO_RESTART')

AD_FALLBACK_TIMEOUT = env_timespan('AD_FALLBACK_TIMEOUT')
FINGERPRINT_SKIP_TIME_AFTER_AD_START = env_timespan('FINGERPRINT_SKIP_TIME_AFTER_AD_START')
FINGERPRINT_SKIP_TIME_AFTER_ARTIFICIAL_AD_END = env_timespan('FINGERPRINT_SKIP_TIME_AFTER_ARTIFICIAL_AD_END')

FINGERPRINT_PIECE_MIN_SIZE = env_size('FINGERPRINT_PIECE_MIN_SIZE')

CLIENT_BUFFER = env_timespan('CLIENT_BUFFER')


