import time
import serial
import logging
from .constants import LockerCommand, PacketByte, ResponseIndex
from .exceptions import LockerException

class Locker:
    MAX_LOCKER = 16
    MIN_LOCKER = 1
    RESPONSE_LENGTH = 9

    def __init__(self, port: str):
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=19200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            logging.info(f"Serial port {port} connected")
        except serial.SerialException as e:
            logging.error(f"Failed to connect to port {port}: {str(e)}")
            raise LockerException(f"Port connection failed: {str(e)}")

    def close(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            logging.info("Serial connection closed")

    def is_locked(self, locker_number: int) -> bool:
        if not self.MIN_LOCKER <= locker_number <= self.MAX_LOCKER:
            error_msg = f"Invalid locker number: {locker_number} (must be {self.MIN_LOCKER}-{self.MAX_LOCKER})"
            logging.error(error_msg)
            raise LockerException(error_msg)

        try:
            cmd = bytearray([
                PacketByte.STX.value,
                PacketByte.DEFAULT_ADDR.value,
                LockerCommand.STATUS.value,
                PacketByte.ETX.value,
                0x35
            ])
            self.ser.write(cmd)
            logging.debug(f"Sent status check command for locker {locker_number}")

            response = self.ser.read(self.RESPONSE_LENGTH)
            if len(response) != self.RESPONSE_LENGTH:
                logging.error(f"Invalid response length: {len(response)}")
                raise LockerException("Status check failed: Invalid response length")

            if response[ResponseIndex.STX.value] != PacketByte.STX.value:
                logging.error("Invalid start byte in response")
                raise LockerException("Status check failed: Invalid start byte")

            status_idx = ResponseIndex.STATUS_1_8.value if locker_number <= 8 else ResponseIndex.STATUS_9_16.value
            bit_position = (locker_number - 1) % 8
            is_locked = bool((response[status_idx] >> bit_position) & 0x01)

            logging.debug(f"Locker {locker_number} status: {'Locked' if is_locked else 'Unlocked'}")
            return is_locked

        except serial.SerialException as e:
            logging.error(f"Communication error during status check: {str(e)}")
            raise LockerException(f"Communication error: {str(e)}")

    def open(self, locker_number: int) -> bool:
        if not self.MIN_LOCKER <= locker_number <= self.MAX_LOCKER:
            error_msg = f"Invalid locker number: {locker_number} (must be {self.MIN_LOCKER}-{self.MAX_LOCKER})"
            logging.error(error_msg)
            raise LockerException(error_msg)

        try:
            if not self.is_locked(locker_number):
                logging.info(f"Locker {locker_number} is already unlocked")
                return True

            packet = bytearray([
                PacketByte.STX.value,
                locker_number - 1,
                LockerCommand.UNLOCK.value,
                PacketByte.ETX.value
            ])
            packet.append(sum(packet) & 0xFF)

            self.ser.write(packet)
            logging.debug(f"Sent unlock command for locker {locker_number}")
            time.sleep(0.025)

            success = not self.is_locked(locker_number)
            if success:
                logging.info(f"Successfully opened locker {locker_number}")
            else:
                logging.error(f"Failed to open locker {locker_number}")
            return success

        except serial.SerialException as e:
            logging.error(f"Communication error during unlock: {str(e)}")
            raise LockerException(f"Communication error: {str(e)}")

    def open_all(self) -> bool:
        success = True
        failed_lockers = []

        for i in range(self.MIN_LOCKER, self.MAX_LOCKER + 1):
            try:
                if not self.open(i):
                    success = False
                    failed_lockers.append(i)
            except LockerException as e:
                logging.error(f"Failed to open locker {i}: {str(e)}")
                success = False
                failed_lockers.append(i)

        if failed_lockers:
            logging.error(f"Failed to open lockers: {failed_lockers}")
        else:
            logging.info("Successfully opened all lockers")

        return success
