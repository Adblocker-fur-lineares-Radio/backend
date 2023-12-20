import logging
import os
import csv
from datetime import datetime
import threading

file_lock = threading.Lock()


# TODO: CLEAN UP CODE AND TEST FUTHER

def configure_logging():
    """
    Initiates Pythons logging library and creates the appropriate file structure
    @return: -
    """
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


def calculate_time_difference_seconds(datetime_str1, datetime_str2):
    """
    Calculates the absolute difference between 2 datetime strings
    @param datetime_str1: string 1 to compare
    @param datetime_str2: string 2 to compare
    @return: the time difference in seconds or None
    """
    format_str = '%m/%d/%Y %I:%M:%S %p'
    try:
        datetime1 = datetime.strptime(datetime_str1, format_str)
        datetime2 = datetime.strptime(datetime_str2, format_str)

        time_difference_seconds = abs((datetime2 - datetime1).total_seconds())

        return time_difference_seconds
    except Exception as e:
        logger.error("ERROR IN CALCULATING TIME DIFFERENCE " + str(e))
        return None


def listify(raw):
    """
    Takes a csv row string and splits it
    @param raw: the raw string
    @return: the string as a list
    """
    try:
        return raw.split(';')
    except Exception as e:
        logger.error("ERROR IN LISTIFY " + str(e))


def check_for_duplicate(rowdata, filepath):
    """
    Checks if the last logged ad is the same that is logged currently,
     to stop double logging from both parallel fingerprint loops
    @param rowdata: the rowdata thats to be inserted
    @param filepath: the appropriate filepath
    @return: if the entry already exists
    """
    if filepath == '/logs/adtime.csv':

        row_list = read_line(rowdata, filepath)
        if row_list is not None:
            i = 0
            for entry in row_list:
                latest_row_entry = listify(entry[i])
                if check_for_same_station_and_flag(rowdata, latest_row_entry):
                    return True
                i += 1
    return False


def check_for_same_station_and_flag(rowdata, latest_row):
    stationID = rowdata[1]
    typeflag = rowdata[2]

    if stationID == latest_row[1]:
        if typeflag == latest_row[2]:

            return True
    return False


def read_line(rowdata, filepath):
    """
    Reads the last line in the csv file
    @param rowdata: the rowdata to be inserted
    @param filepath: the appropriate filepath
    @return: the line as a list with one element or None
    """
    try:
        with open(filepath, 'r', newline='') as file:
            linelist = []
            reader = csv.reader(file)
            i = 0

            csvlines = list(reader)
            if len(csvlines) > 0:
                temp = csvlines.pop(0)
                csvlines = reversed(csvlines)

                for row in csvlines:
                    if check_in_time_window(rowdata, row):
                        linelist.append(row)
                        i += 1
                    else:
                        return None
                if i > 0:
                    return linelist
    except Exception as e:
        logger.error("ERROR IN READING LAST LINE " + str(e))
    return None


def check_in_time_window(rowdata, csvline):
    csvline = listify(csvline[0])
    try:
        if calculate_time_difference_seconds(rowdata[0], csvline[0]) <= 8:
            return True
    except Exception as e:
        logger.error("ERROR IN CHECK IN TIME WINDOW " + str(e))
    return False


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
    header = ['date', 'stationID', 'typeflag']
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

    currenttime = datetime.now()
    formattedtime = currenttime.strftime("%m/%d/%Y %I:%M:%S %p")

    rowdata.insert(0, formattedtime)

    if data is not None:
        try:
            with file_lock:
                with open(filename, 'a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=';')
                    if not check_for_duplicate(rowdata, filename):
                        csv_writer.writerow(data)
                    csv_file.flush()
        except Exception as e:
            logger.error("ERROR IN WRITE " + str(e))
            raise e
    return
