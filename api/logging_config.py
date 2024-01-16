import logging
import os
import csv
import threading
from pytz import timezone
from datetime import datetime

file_lock = threading.Lock()


def configure_logging():
    """
    Initiates Pythons logging library and creates the appropriate file structure
    @return: -
    """
    logs_directory = os.path.abspath(os.path.join(os.getcwd(), 'logs'))
    os.makedirs(logs_directory, exist_ok=True)
    log_file_path = '/logs/backend.log'
    logging.Formatter.converter = lambda *args: datetime.now(tz=timezone('Europe/Berlin')).timetuple()
    logging.basicConfig(format='%(levelname)s %(asctime)s %(name)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        encoding='utf-8',
                        level=logging.INFO,
                        handlers=[
                            logging.FileHandler(log_file_path),
                            logging.StreamHandler()
                        ]
                        )


configure_logging()
logger = logging.getLogger("logging_config.py")


def csv_logging_setup():
    """
    Sets up the csv logging for the metadata and adtime
    @return: -
    """
    logs_directory = os.path.abspath(os.path.join(os.getcwd(), 'logs'))
    os.makedirs(logs_directory, exist_ok=True)
    metadate_logging_init()
    adtime_logging_init()


def metadate_logging_init():
    """
    Creates the appropriate metadata.csv file with header data
    @return: -
    """
    filename = '/logs/metadata.csv'
    header = ['date', 'stationID', 'interpret', 'title']
    try:
        with file_lock:
            with open(filename, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';')
                if csv_file.tell() == 0:
                    csv_writer.writerow(header)
                csv_file.flush()
    except Exception as e:
        logger.error("ERROR IN METADATA HEADERWRITE " + str(e))
        raise e


def adtime_logging_init():
    """
    Creates the appropriate adtime.csv file with header data
    @return: -
    """
    filename = '/logs/adtime.csv'
    header = ['date', 'stationName', 'typeflag']
    try:
        with file_lock:
            with open(filename, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';')
                if csv_file.tell() == 0:
                    csv_writer.writerow(header)
                csv_file.flush()
    except Exception as e:
        logger.error("ERROR IN ADTIME HEADERWRITE " + str(e))
        raise e


def csv_logging_write(data, pathname):
    """
    Writes a csv row to the specified file
    @param data: a list of csvfile attributes
    @param pathname: the filename (not fullpath) to be logged to
    @return: -
    """
    filename = '/logs/' + pathname

    rowdata = data

    currenttime = datetime.now(tz=timezone('Europe/Berlin'))
    formattedtime = currenttime.strftime("%m/%d/%Y %H:%M:%S")

    rowdata.insert(0, formattedtime)

    if data is not None:
        try:
            with file_lock:
                with open(filename, 'a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=';')
                    csv_writer.writerow(data)
                    csv_file.flush()
        except Exception as e:
            logger.error("ERROR IN WRITE " + str(e))
            raise e
    return
