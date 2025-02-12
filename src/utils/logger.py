import logging
import os
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

    # 에러 로그 설정 (ERROR) - backupCount 제거하여 계속 보관
    error_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'error.log'),
        when='midnight',
        interval=1,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('\n[%(asctime)s]\nERROR: %(message)s\n' + '-'*50)
    error_handler.setFormatter(error_formatter)
    logging.getLogger().addHandler(error_handler)

    # 콘솔 출력 설정
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(general_formatter)
    logging.getLogger().addHandler(console_handler)

    logging.getLogger().setLevel(log_level)
