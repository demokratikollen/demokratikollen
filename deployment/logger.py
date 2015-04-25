import logging
import sys


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
 
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

def setup_logging(base_dir):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(base_dir + 'deploy.log', encoding='UTF-8')
    fh.setFormatter(logging.Formatter('[%(levelname)8s] %(message)s'))
    root_logger.addHandler(fh)

    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl
 
    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl

