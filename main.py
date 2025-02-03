from src.locker import Locker, LockerException
from src.logger_config import setup_logger


def main():
    # 로거 설정
    logger = setup_logger()
    locker = None
    port = 'COM6'

    try:
        locker = Locker(port, verbose=True)

        # 상태 확인
        status = locker.is_locked(1)
        logger.info(f"1번 사물함 상태: {'잠김' if status else '열림'}")

        # 열기 시도
        if status:
            success = locker.open(1)
            logger.info(f"1번 사물함 열기: {'성공' if success else '실패'}")

    except LockerException as e:
        logger.error(f"사물함 오류: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        raise
    finally:
        if locker:
            locker.close()


if __name__ == "__main__":
    main()
