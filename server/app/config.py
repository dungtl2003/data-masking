from uvicorn.logging import DefaultFormatter, AccessFormatter

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s [PID: %(process)d, Process: %(processName)s]: %(message)s"
        },
        "default": {
            "()": DefaultFormatter,
            "fmt": "%(asctime)s %(levelprefix)-9s %(name)s [PID: %(process)d, Process: %(processName)s] -: %(message)s",
        },
        "access": {
            "()": AccessFormatter,
            "fmt": '%(asctime)s %(levelprefix)-9s %(name)s [PID: %(process)d, Process: %(processName)s] -: %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {
            "level": "DEBUG",
            "handlers": ["default"],
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "level": "INFO",
            "propagate": False,
            "handlers": ["access"],
        },
    },
}
