import pytest
from src.locker import Locker, LockerException
from src.logger_config import setup_logger

# 사물함 시리얼 포트 설정
# Serial port configuration for locker
LOCKER_PORT = 'COM6'


@pytest.fixture(autouse=True)
def setup_logging():
    """
    로깅 설정을 초기화하는 픽스처
    Fixture to initialize logging configuration
    """
    setup_logger()


@pytest.fixture
def locker():
    """
    테스트용 사물함 객체를 생성하고 관리하는 픽스처
    Fixture to create and manage locker object for testing
    """
    locker = Locker(LOCKER_PORT)
    yield locker
    locker.close()


def test_connection_success():
    """
    시리얼 포트 연결 성공 테스트
    Test for successful serial port connection
    """
    locker = Locker(LOCKER_PORT)
    assert locker.ser is not None
    assert locker.ser.port == LOCKER_PORT
    locker.close()


def test_connection_failure():
    """
    잘못된 포트로 연결 실패 테스트
    Test for connection failure with invalid port
    """
    with pytest.raises(LockerException, match="포트 연결 실패"):
        Locker('INVALID_PORT')


def test_close_connection(locker):
    """
    연결 종료 기능 테스트
    Test for connection closing functionality
    """
    locker.close()
    assert not locker.ser.is_open


@pytest.mark.parametrize("locker_number", range(1, 17))
def test_status_check(locker, locker_number):
    """
    각 사물함의 상태 확인 테스트
    Test for checking status of each locker

    Args:
        locker_number: 테스트할 사물함 번호 (1-16)
                      Locker number to test (1-16)
    """
    status = locker.is_locked(locker_number)
    assert isinstance(status, bool)
    print(f"Locker {locker_number} status: {'Locked' if status else 'Unlocked'}")


@pytest.mark.parametrize("invalid_number", [-1, 0, 17, 100])
def test_invalid_locker_number(locker, invalid_number):
    """
    잘못된 사물함 번호 입력 테스트
    Test for invalid locker number input

    Args:
        invalid_number: 테스트할 잘못된 사물함 번호
                       Invalid locker number to test
    """
    with pytest.raises(LockerException, match="잘못된 사물함 번호"):
        locker.is_locked(invalid_number)


def test_open_locker(locker):
    """
    단일 사물함 열기 테스트
    Test for opening a single locker
    """
    locker_number = 1
    initial_status = locker.is_locked(locker_number)
    print(f"Initial status of locker {locker_number}: {'Locked' if initial_status else 'Unlocked'}")

    if initial_status:
        result = locker.open(locker_number)
        assert result
        final_status = locker.is_locked(locker_number)
        assert not final_status
        print(f"Locker {locker_number} opened successfully")


def test_open_already_unlocked(locker):
    """
    이미 열린 사물함 열기 시도 테스트
    Test for attempting to open an already unlocked locker
    """
    locker_number = 1
    if not locker.is_locked(locker_number):
        result = locker.open(locker_number)
        assert result
        print(f"Locker {locker_number} was already unlocked")


def test_open_all(locker):
    """
    전체 사물함 열기 테스트
    Test for opening all lockers
    """
    # 전체 열기 시도
    # Attempt to open all lockers
    result = locker.open_all()
    assert isinstance(result, bool)

    # 전체 상태 확인
    # Check status of all lockers
    statuses = []
    for i in range(1, 17):
        status = locker.is_locked(i)
        statuses.append(status)
        print(f"Locker {i} status after open_all: {'Locked' if status else 'Unlocked'}")

    print(f"All locker statuses: {statuses}")
