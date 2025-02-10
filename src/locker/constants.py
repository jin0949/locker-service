from enum import Enum

class LockerCommand(Enum):
    """
    사물함 제어 명령어
    Locker control commands
    """
    STATUS = 0x30  # 상태 확인 명령 / Status check command
    UNLOCK = 0x31  # 잠금 해제 명령 / Unlock command

class PacketByte(Enum):
    """
    패킷 구조 바이트
    Packet structure bytes
    """
    STX = 0x02  # 시작 바이트 / Start byte
    ETX = 0x03  # 종료 바이트 / End byte
    DEFAULT_ADDR = 0x00  # 기본 주소 / Default address

class ResponseIndex(Enum):
    """
    응답 패킷 인덱스
    Response packet indices
    """
    STX = 0           # 시작 바이트 위치 / Start byte position
    ADDR = 1          # 주소 위치 / Address position
    CMD = 2           # 명령어 위치 / Command position
    STATUS_1_8 = 3    # 1-8번 사물함 상태 위치 / Status for lockers 1-8
    STATUS_9_16 = 4   # 9-16번 사물함 상태 위치 / Status for lockers 9-16
    ETX = 5           # 종료 바이트 위치 / End byte position
    RESERVED1 = 6     # 예약된 바이트 1 / Reserved byte 1
    RESERVED2 = 7     # 예약된 바이트 2 / Reserved byte 2
    CHECKSUM = 8      # 체크섬 위치 / Checksum position
