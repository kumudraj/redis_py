import datetime
import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler

default_log_file = "../logs/history.logs".replace('.log',
                                                  '_' + str(datetime.datetime.today().strftime('%Y_%m_%d')) + '.log')

ERROR = 3
WARNING = 2
INFO = 1
DEBUG = 0


class LoggingModule:
    __slots__ = ('name', 'log_file_loc', 'debug_level', 'logger')

    def __init__(self, name=None, log_file_loc=None, debug_level=0):
        if name is None:
            raise Exception("Expected parameter: name, logfileloc and optional parameter debug_level ")
        if log_file_loc is None:
            self.log_file_loc = default_log_file
        else:
            self.log_file_loc = log_file_loc
        self.name = name
        self.debug_level = debug_level
        self.getlogger()

    def getlogger(self):
        backupCount = 10
        self.logger = logging.getLogger(self.name)
        if self.debug_level == 0:
            self.logger.setLevel(logging.DEBUG)
        if self.debug_level == 1:
            self.logger.setLevel(logging.INFO)
        if self.debug_level == 2:
            self.logger.setLevel(logging.ERROR)

        handler = logging.handlers.TimedRotatingFileHandler(self.log_file_loc,
                                                            when="d",
                                                            interval=1,
                                                            backupCount=backupCount)

        streamhandler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] p%(process)s %(levelname)s - %(message)s',
                                      '%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        streamhandler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.addHandler(streamhandler)

        logger_obj = self.logger
        logger_obj.propagate = False
        return logger_obj

    def log_message(self, log_state, *args):
        if log_state == ERROR:
            self.logger.handlers[-1].stream = sys.stderr
            self.logger.error(args)
        elif log_state == WARNING:
            self.logger.handlers[-1].stream = sys.stderr
            self.logger.warning(args)
        elif log_state == INFO:
            self.logger.handlers[-1].stream = sys.stdout
            self.logger.info(args)
        else:
            self.logger.handlers[-1].stream = sys.stdout
            self.logger.debug(args)


def error_logging(var, next_frame=False):
    error_type = var[0].__name__
    error_msg = var[1]
    if next_frame:
        source = (
            os.path.split(var[2].tb_next.tb_frame.f_code.co_filename)[1],
            sys.exc_info()[2].tb_next.tb_lineno
        )
    else:
        source = (
            os.path.split(var[2].tb_frame.f_code.co_filename)[1],
            var[2].tb_lineno
        )
    return {'Type': error_type, 'Msg': error_msg, 'Source': source}


def get_time():
    return time.time()


def info_msg(name=None, time_taken=None, msg=None, source=None):
    if name and time_taken:
        return "{} takes {:f} seconds in processing request. , {}".format(name, time_taken,
                                                                          (os.path.basename(
                                                                              str(source.f_code.co_filename)),
                                                                           source.f_lineno))
    else:
        return "{}, {}".format(msg, (os.path.basename(str(source.f_code.co_filename)), source.f_lineno))
