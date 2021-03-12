LOGGING_CONFIG = {
        'version': 1,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(asctime)s  %(message)s',
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
        },
        'disable_existing_loggers': False,

        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
                },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': '../logs/i18n.log'.format(),
                'maxBytes': 1024*1024*1,
                'backupCount': 10,
                'formatter': 'simple'
                },
        },
        'root': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'loggers': {
            'utils': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            }
        }
    }