import logging
import os
import csv
from datetime import datetime


def configure_logging():
    logs_directory = os.path.abspath(os.path.join(os.getcwd(), 'logs'))
    os.makedirs(logs_directory, exist_ok=True)
    log_file_path = '/logs/backend.log'
    logging.basicConfig(format='%(levelname)s %(asctime)s %(name)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
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
    logs_directory = os.path.abspath(os.path.join(os.getcwd(), 'logs'))
    os.makedirs(logs_directory, exist_ok=True)


def csv_logging_write(data):
    filename = '/logs/metadata.csv'
    header = ['date', 'stationID', 'interpret', 'title']
    rowdata = data
    currenttime = datetime.now()
    formattedtime = currenttime.strftime("%m/%d/%Y %I:%M:%S %p")
    rowdata.insert(0, formattedtime)

    if data is not None:
        try:

            with open(filename, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';')
                if csv_file.tell() == 0:
                    csv_writer.writerow(header)
                csv_writer.writerow(data)
                csv_file.flush()
        except Exception as e:
            logger.error("ERROR IN WRITE")
            raise e
    return
