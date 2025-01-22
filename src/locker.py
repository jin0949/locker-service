import inspect
import time
import serial

## KR-CU16 사물함 중앙장치 제어 코드

class Locker:
    def __init__(
            self,
            port: str,
            verbose: bool=False
    ):
        self.ser = serial.Serial(
            port=port,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        self.debug = verbose

    def close(self):
        """시리얼 포트 연결 종료"""
        self.ser.close()

    def verbose(self, msg):
        """디버그 메시지 출력"""
        if self.debug:
            method = inspect.currentframe().f_back.f_code.co_name
            print(f"\033[96m{method}> \033[92m{msg}\033[0m")

    @staticmethod
    def calc_checksum(data):
        """체크섬 계산"""
        return sum(data) & 0xFF

    def _create_unlock_packet(self, lock_num):
        """잠금해제 패킷 생성"""
        STX = 0x02  # 시작 바이트
        addr = lock_num - 1  # 락커 주소
        CMD = 0x31  # 잠금해제 명령어
        ETX = 0x03  # 종료 바이트

        arr = [STX, addr, CMD, ETX]
        packet = bytearray(arr)
        checksum = self.calc_checksum(arr)
        packet.append(checksum)

        self.verbose(
            f"{packet.hex()} ({len(packet)} bytes)\n"
            f"{arr}\n"
            f"cks: ({checksum})\n"
        )
        return packet

    def _exec_unlock(self, n):
        """락커 잠금해제 실행"""
        if n < 1 or n > 16:
            err = f"Lock number must be between 1 and 16. Provided value: {n}"
            self.verbose(err)
            raise ValueError(err)

        if not self.is_locked(n):
            self.verbose(f"Lock {n} is already unlocked.")
            return False

        cmd = self._create_unlock_packet(n)
        self.verbose(f"Sent Hex: {cmd.hex()}")
        self.ser.write(cmd)

        time.sleep(0.025)

        if self.is_locked(n):
            self.verbose(f"Failed to unlock lock {n}")
            return False
        else:
            self.verbose(f"Lock {n} unlocked successfully.")
            return True

    def open(self, n: int):
        """락커 열기"""
        self.verbose(f"Opening lock {n}...")
        if n <= 0:
            raise ValueError("Lock number must be greater than 0")
        return self._exec_unlock(n)

    def is_locked(self, lock_number):
        """락커 잠금 상태 확인"""
        if lock_number < 1 or lock_number > 16:
            raise ValueError("Invalid lock number. Must be between 1 and 16.")

        cu16_address_hex = 0x00
        self.verbose(f"Checking lock {lock_number}... [CU16 Address: {hex(cu16_address_hex)}]")

        cmd = bytearray([0x02, cu16_address_hex, 0x30, 0x03, 0x35])
        self.ser.write(cmd)

        res = self.ser.read(9)
        time.sleep(0.025)

        self.verbose(f"Received response: {res.hex()}")
        self.verbose(f"Response length: {len(res)}")

        if len(res) == 9:
            stx = res[0]
            self.verbose(f"STX: {hex(stx)}")
            if stx != 0x02:
                raise ValueError("Invalid start byte")

            addr = res[1]
            self.verbose(f"ADDR: {hex(addr)}")
            if addr != cu16_address_hex:
                raise ValueError("Invalid address")

            cmd_res = res[2]
            self.verbose(f"CMD_RES: {hex(cmd_res)}")
            if cmd_res != 0x35:
                raise ValueError("Invalid command response")

            lock_state_1_8 = res[3]
            lock_state_9_16 = res[4]

            self.verbose(f"LOCK_STATUS (1-8): {hex(lock_state_1_8)} [{bin(lock_state_1_8)[2:].zfill(8)}]")
            self.verbose(f"LOCK_STATUS (9-16): {hex(lock_state_9_16)} [{bin(lock_state_9_16)[2:].zfill(8)}]")

            lock_bit = 0

            if 1 <= lock_number <= 8:
                lock_bit = (lock_state_1_8 >> (lock_number - 1)) & 0x01
            elif 9 <= lock_number <= 16:
                lock_bit = (lock_state_9_16 >> (lock_number - 9)) & 0x01

            self.verbose(f"Lock {lock_number} status: {'Locked' if lock_bit == 1 else 'Unlocked'}")
            return lock_bit == 1
        else:
            self.verbose("Invalid response length")
            raise ValueError(f"Invalid response length: {len(res)}")