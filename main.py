from src.locker import Locker


def main():
    try:
        # Windows의 경우 'COM1(맞는포트 장치 드라이버에서 찾아쓰세요.', Linux/Mac의 경우 '/dev/ttyUSB0' 등
        locker = Locker(port='COM1', verbose=True)  # 디버그 메시지 출력을 위해 verbose=True

        # 2. 특정 사물함 상태 확인
        locker_number = 1
        is_locked = locker.is_locked(locker_number)
        print(f"사물함 {locker_number}번 상태: {'잠김' if is_locked else '열림'}")

        # 3. 사물함 열기
        if is_locked:
            success = locker.open(locker_number)
            if success:
                print(f"사물함 {locker_number}번이 성공적으로 열렸습니다.")
            else:
                print(f"사물함 {locker_number}번 열기 실패")

    except ValueError as e:
        print(f"에러 발생: {e}")
    except serial.SerialException as e:
        print(f"시리얼 통신 에러: {e}")
    finally:
        # 4. 연결 종료
        if 'locker' in locals():
            locker.close()


if __name__ == "__main__":
    main()
