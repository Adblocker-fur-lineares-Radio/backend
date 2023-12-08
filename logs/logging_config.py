import logging
import os
cwd = os.getcwd()
parent_directory = os.path.abspath(os.path.join(cwd, os.pardir))




def configure_logging():
    logging.basicConfig(format='%(levelname)s %(asctime)s %(name)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename=parent_directory+'/logs/backend.log',
                        encoding='utf-8',
                        level=logging.INFO
                        )
