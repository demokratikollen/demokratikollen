import logging

def get_logger(base_dir):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    #ch = logging.StreamHandler()
    #ch.setFormatter(logging.Formatter('[%(levelname)8s] %(message)s'))
    fh = logging.FileHandler(base_dir + 'deploy.log')
    fh.setFormatter(logging.Formatter('[%(levelname)8s] %(message)s'))

    logger.addHandler(fh)
    return logger
