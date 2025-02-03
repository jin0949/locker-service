import time
import serial
import logging
from .constants import LockerCommand, PacketByte, ResponseIndex
from .exceptions import LockerException

class Locker:
    """
    사물함 제어 클래스
    Locker control class
    """
    MAX_LOCKER = 16   # 최대 사물함 번호 / Maximum locker number
    MIN_LOCKER = 1    # 최소 사물함 번호 / Minimum locker number
    RESPONSE_LENGTH = 9  # 응답 패킷 길이 / Response packet length

    def __init__(self, port: str):
        """
        사물함 제어 초기화
        Initialize locker control
        """
        self.logger = logging.getLogger('locker_system')

        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=19200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            self.logger.info(f"포트 {port} 연결 성공 / Port {port} connection successful")
        except serial.SerialException as e:
            self.logger.error(f"포트 {port} 연결 실패 / Port {port} connection failed: {str(e)}")
            raise LockerException(f"포트 연결 실패 / Port connection failed: {str(e)}")

    def close(self):
        """
        시리얼 포트 연결 종료
        Close serial port connection
        """
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            self.logger.info("연결 종료 / Connection closed")

    def is_locked(self, locker_number: int) -> bool:
        """
        사물함 잠금 상태 확인
        Check if locker is locked
        """
        if not self.MIN_LOCKER <= locker_number <= self.MAX_LOCKER:
            raise LockerException(
                f"잘못된 사물함 번호 / Invalid locker number: {locker_number} "
                f"({self.MIN_LOCKER}-{self.MAX_LOCKER} 사이 값 필요 / value must be between {self.MIN_LOCKER}-{self.MAX_LOCKER})"
            )

        try:
            cmd = bytearray([
                PacketByte.STX.value,
                PacketByte.DEFAULT_ADDR.value,
                LockerCommand.STATUS.value,
                PacketByte.ETX.value,
                0x35  # Checksum for status command
            ])
            self.ser.write(cmd)

            response = self.ser.read(self.RESPONSE_LENGTH)
            if len(response) != self.RESPONSE_LENGTH:
                raise LockerException("상태 확인 실패: 잘못된 응답 길이 / Status check failed: Invalid response length")

            if response[ResponseIndex.STX.value] != PacketByte.STX.value:
                raise LockerException("상태 확인 실패: 잘못된 시작 바이트 / Status check failed: Invalid start byte")

            status_idx = ResponseIndex.STATUS_1_8.value if locker_number <= 8 else ResponseIndex.STATUS_9_16.value
            bit_position = (locker_number - 1) % 8
            is_locked = bool((response[status_idx] >> bit_position) & 0x01)

            if self.verbose:
                self.logger.debug(
                    f"사물함 {locker_number} 상태 / Locker {locker_number} status: "
                    f"{'잠김 / Locked' if is_locked else '열림 / Unlocked'}"
                )
            return is_locked

        except serial.SerialException as e:
            raise LockerException(f"통신 오류 / Communication error: {str(e)}")

    def open(self, locker_number: int) -> bool:
        """
        사물함 열기
        Open locker
        """
        if not self.MIN_LOCKER <= locker_number <= self.MAX_LOCKER:
            raise LockerException(
                f"잘못된 사물함 번호 / Invalid locker number: {locker_number} "
                f"({self.MIN_LOCKER}-{self.MAX_LOCKER} 사이 값 필요 / value must be between {self.MIN_LOCKER}-{self.MAX_LOCKER})"
            )

        try:
            if not self.is_locked(locker_number):
                self.logger.info(f"사물함 {locker_number}번이 이미 열려있습니다 / Locker {locker_number} is already unlocked")
                return True

            packet = bytearray([
                PacketByte.STX.value,
                locker_number - 1,
                LockerCommand.UNLOCK.value,
                PacketByte.ETX.value
            ])
            packet.append(sum(packet) & 0xFF)  # Checksum

            self.ser.write(packet)
            time.sleep(0.025)

            success = not self.is_locked(locker_number)
            if success:
                self.logger.info(f"사물함 {locker_number}번 열기 성공 / Successfully opened locker {locker_number}")
            else:
                self.logger.error(f"사물함 {locker_number}번 열기 실패 / Failed to open locker {locker_number}")
            return success

        except serial.SerialException as e:
            raise LockerException(f"통신 오류 / Communication error: {str(e)}")

    def open_all(self) -> bool:
        """
        모든 사물함 열기
        Open all lockers
        """
        success = True
        failed = []

        for i in range(self.MIN_LOCKER, self.MAX_LOCKER + 1):
            try:
                if not self.open(i):
                    success = False
                    failed.append(i)
            except LockerException as e:
                self.logger.error(f"사물함 {i}번 열기 실패 / Failed to open locker {i}: {str(e)}")
                success = False
                failed.append(i)

        if failed:
            self.logger.warning(f"열기 실패한 사물함 / Failed to open lockers: {failed}")
        else:
            self.logger.info("모든 사물함 열기 성공 / Successfully opened all lockers")

        return success
