import logging
from datetime import datetime


def setup_logger(file_logging: bool = False):
    """
    로거 설정
    Logger configuration

    Args:
        file_logging (bool): 파일 로깅 활성화 여부 / Enable file logging
    """
    logger = logging.getLogger('locker_system')
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 콘솔 로깅 설정 / Console logging setup
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 파일 로깅 설정 / File logging setup
        if file_logging:
            file_handler = logging.FileHandler(
                f'locker_{datetime.now().strftime("%Y%m%d")}.log'
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
