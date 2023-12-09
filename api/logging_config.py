import logging
import os




def configure_logging():
    logs_directory = os.path.abspath(os.path.join(os.getcwd(), 'logs'))


    os.makedirs(logs_directory, exist_ok=True)


    log_file_path = os.path.join(logs_directory, '../logs/backend.log')
    logging.basicConfig(format='%(levelname)s %(asctime)s %(name)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename=log_file_path,
                        encoding='utf-8',
                        level=logging.INFO
                        )
