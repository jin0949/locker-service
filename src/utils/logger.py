import logging
import os
import colorlog
from logging.handlers import TimedRotatingFileHandler

def setup_logger(log_dir='logs', log_level=logging.INFO):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 기존 핸들러 제거
    logging.getLogger().handlers.clear()

    # 일반 로그 설정 (INFO, WARNING)
    general_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'service.log'),
        when='midnight',
        interval=1,
        backupCount=1,
        encoding='utf-8'
    )
    general_handler.setLevel(logging.INFO)
    general_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    general_handler.setFormatter(general_formatter)
    general_filter = lambda record: record.levelno < logging.ERROR
    general_handler.addFilter(general_filter)
    logging.getLogger().addHandler(general_handler)

    # 에러 로그 설정 (ERROR)
    error_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'error.log'),
        when='midnight',
        interval=1,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('\n[%(asctime)s]\nERROR: %(message)s\n' + '-'*50)
    error_handler.setFormatter(error_formatter)
    error_filter = lambda record: record.levelno == logging.ERROR
    error_handler.addFilter(error_filter)
    logging.getLogger().addHandler(error_handler)

    # 크리티컬 로그 설정 (CRITICAL)
    critical_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'critical.log'),
        when='midnight',
        interval=1,
        encoding='utf-8'
    )
    critical_handler.setLevel(logging.CRITICAL)
    critical_formatter = logging.Formatter('\n[%(asctime)s]\nCRITICAL: %(message)s\n' + '-'*50)
    critical_handler.setFormatter(critical_formatter)
    logging.getLogger().addHandler(critical_handler)

    # 컬러 콘솔 출력 설정
    console_handler = colorlog.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s[%(asctime)s] %(levelname)s: %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)

    logging.getLogger().setLevel(log_level)
