# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

class TweepyLogger(object):

    DEBUG = 1
    WARNING = 2
    ERROR = 3

    def debug(self, message):
        """Output a debug log message"""
        self.log(TweepyLogger.DEBUG, message)

    def warning(self, message):
        """Output warning log message"""
        self.log(TweepyLogger.WARNING, message)

    def error(self, message):
        """Output error log message"""
        self.log(TweepyLogger.ERROR, message)

    def log(self, level, message):
        """Implement this method to handle log messages"""
        raise NotImplementedError

    def format(self, message):
        """Override this method to apply custom formating of messages"""
        return message

class DummyLogger(TweepyLogger):
    """This logger just discards log messages"""

    def log(self, level, message):
        return

class ConsoleLogger(TweepyLogger):
    """Outputs log messages to stdout"""

    def __init__(self, active_log_level=TweepyLogger.DEBUG):
        self.active_log_level = active_log_level

    def log(self, level, message):
        if level <= self.active_log_level:
            print message

class FileLogger(TweepyLogger):
    """Outputs log message to file"""

    def __init__(self, filepath, active_log_level=TweepyLogger.DEBUG):
        self.active_log_level = active_log_level
        self.file = open(filepath, 'w')

    def log(self, level, message):
        if level <= self.active_log_level:
            self.file.write(message + '\n')
            self.file.flush()

