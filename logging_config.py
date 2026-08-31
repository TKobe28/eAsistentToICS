import logging
import logging.config
import colorlog

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(asctime)s [%(levelname)s]%(reset)s %(name)s: %(message)s',
            'log_colors': {
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            },
        },
        'standard': {  # keep plain format for file output
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'root': {
        'handlers': ['console',],
        'level': 'INFO',
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    setup_logging()
    levels = (
        (logging.CRITICAL, "CRITICAL"),
        (logging.FATAL, "FATAL"),
        (logging.ERROR, "ERROR"),
        (logging.WARNING, "WARNING"),
        (logging.WARN, "WARN"),
        (logging.INFO, "INFO"),
        (logging.DEBUG, "DEBUG"),
        (logging.NOTSET, "NOTSET"),
    )

    for level_int, level_name in levels:
        logger.log(level_int, f"This is log level {level_name} ({level_int})!")
