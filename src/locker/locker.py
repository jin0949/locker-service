import logging
import time
import serial
from .constants import LockerCommand, PacketByte, ResponseIndex

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
            logging.info(f"Serial port {port} connected successfully")
        except serial.SerialException as e:
            raise Exception(f"Port connection failed: {str(e)}")

    def close(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            logging.debug("Serial connection closed properly")

    def get_all_locker_states(self) -> dict:
        """
        Get the status of all lockers at once
        Returns a dictionary with locker numbers as keys and locked status as values
        """
        try:
            cmd = bytearray([
                PacketByte.STX.value,
                PacketByte.DEFAULT_ADDR.value,
                LockerCommand.STATUS.value,
                PacketByte.ETX.value,
                0x35
            ])
            self.ser.write(cmd)
            logging.debug("Checking status of all lockers")

            response = self.ser.read(self.RESPONSE_LENGTH)
            if len(response) != self.RESPONSE_LENGTH:
                logging.error(f"Invalid response length from hardware: {len(response)}")
                return {i: True for i in range(self.MIN_LOCKER, self.MAX_LOCKER + 1)}

            if response[ResponseIndex.STX.value] != PacketByte.STX.value:
                logging.error("Hardware communication error: Invalid start byte")
                return {i: True for i in range(self.MIN_LOCKER, self.MAX_LOCKER + 1)}

            states = {}
            # Process lockers 1-8
            for i in range(8):
                states[i + 1] = bool((response[ResponseIndex.STATUS_1_8.value] >> i) & 0x01)
            # Process lockers 9-16
            for i in range(8):
                states[i + 9] = bool((response[ResponseIndex.STATUS_9_16.value] >> i) & 0x01)

            logging.debug(f"All locker states retrieved: {states}")
            return states

        except serial.SerialException as e:
            logging.error(f"Hardware communication failure: {str(e)}")
            return {i: True for i in range(self.MIN_LOCKER, self.MAX_LOCKER + 1)}
        except Exception as e:
            logging.error(f"Unexpected error while checking locker status: {str(e)}")
            return {i: True for i in range(self.MIN_LOCKER, self.MAX_LOCKER + 1)}

    def is_locked(self, locker_number: int) -> bool:
        if not self.MIN_LOCKER <= locker_number <= self.MAX_LOCKER:
            logging.error(f"Invalid locker number: {locker_number} (valid range: {self.MIN_LOCKER}-{self.MAX_LOCKER})")
            return True

        states = self.get_all_locker_states()
        return states.get(locker_number, True)

    def open(self, locker_number: int) -> bool:
        if not self.MIN_LOCKER <= locker_number <= self.MAX_LOCKER:
            logging.error(f"Invalid locker number: {locker_number} (valid range: {self.MIN_LOCKER}-{self.MAX_LOCKER})")
            return False

        try:
            if not self.is_locked(locker_number):
                logging.debug(f"Locker {locker_number} is already in unlocked state")
                return True

            packet = bytearray([
                PacketByte.STX.value,
                locker_number - 1,
                LockerCommand.UNLOCK.value,
                PacketByte.ETX.value
            ])
            packet.append(sum(packet) & 0xFF)

            self.ser.write(packet)
            logging.debug(f"Sent unlock command to locker {locker_number}")
            time.sleep(0.025)

            success = not self.is_locked(locker_number)
            if success:
                logging.debug(f"Locker {locker_number} unlocked successfully")
            else:
                logging.error(f"Failed to unlock locker {locker_number}")
            return success

        except serial.SerialException as e:
            logging.error(f"Hardware communication failure during unlock: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error while unlocking locker: {str(e)}")
            return False

    def open_all(self) -> bool:
        success = True
        failed_lockers = []

        for i in range(self.MIN_LOCKER, self.MAX_LOCKER + 1):
            if not self.open(i):
                success = False
                failed_lockers.append(i)

        if failed_lockers:
            logging.error(f"Failed to open lockers: {failed_lockers}")
        else:
            logging.debug("All lockers opened successfully")

        return success