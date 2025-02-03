# KR-CU16 Locker Control System
# KR-CU16 사물함 제어 시스템

GitHub Repository: https://github.com/jin0949/KR-CU16_locker

This project provides a Python interface for controlling the KR-CU16 locker system.
이 프로젝트는 KR-CU16 사물함 시스템을 제어하기 위한 파이썬 인터페이스를 제공합니다.

## Hardware Requirements / 하드웨어 요구사항

- KR-CU16 locker control unit
- KR-CU16 사물함 제어 장치
- RS485 to USB converter
- RS485-USB 컨버터
- 12V 2.5A power adapter (Sky brand adapter shown in image)
- 12V 2.5A 전원 어댑터 (이미지의 Sky 브랜드 어댑터)

## Hardware Connection / 하드웨어 연결

### KR-CU16 Layout / KR-CU16 구성:

- Left side: Lockers 1-8 with LED indicators
- 왼쪽: LED 표시등이 있는 1-8번 사물함
- Right side: Lockers 9-16 with LED indicators
- 오른쪽: LED 표시등이 있는 9-16번 사물함
- Power input: 2-pin connector for 12V 2.5A
- 전원 입력: 12V 2.5A용 2핀 커넥터
- Serial port: USB connection via RS485 converter
- 시리얼 포트: RS485 컨버터를 통한 USB 연결
  
![KakaoTalk_20250203_155519486](https://github.com/user-attachments/assets/50f9f633-dad8-4a32-bb95-836deb9a8d79)

### RS485-USB Connection / RS485-USB 연결
For USB connectivity, you'll need to directly wire and connect using an RS485 to USB converter. I used the converter shown in the picture.
USB 연결을 위해서는 RS485-USB 컨버터를 이용하여 직접 배선 연결이 필요합니다. 사진에 보이는 컨버터를 사용했습니다.

![KakaoTalk_20250203_165724242](https://github.com/user-attachments/assets/0d8d3c40-b4a6-4d66-86ed-4f70b4fc4e57)

## Software Installation / 소프트웨어 설치

```bash
git clone https://github.com/jin0949/KR-CU16_locker.git
cd KR-CU16_locker
pip install -r requirements.txt
```

## Usage / 사용 방법

```python
from src.locker import Locker
from src.logger_config import setup_logger

# Initialize logger / 로거 초기화
logger = setup_logger()

# Connect to locker system / 사물함 시스템 연결
locker = Locker('COM6')

# Check locker status / 사물함 상태 확인
status = locker.is_locked(1)

# Open specific locker / 특정 사물함 열기
success = locker.open(1)

# Open all lockers / 전체 사물함 열기
success = locker.open_all()
```

## Features / 기능

- Individual locker status checking
- 개별 사물함 상태 확인
- Single locker control
- 단일 사물함 제어
- All locker control
- 전체 사물함 제어
- Error handling and logging
- 에러 처리 및 로깅

## Notes / 참고사항

- The system uses RS485 protocol for communication
- 시스템은 RS485 프로토콜을 사용하여 통신합니다
- LED indicators show locker status (optional feature)
- LED 표시등으로 사물함 상태 표시 (선택 기능)
- Compatible with Windows COM ports
- Windows COM 포트와 호환됩니다

## License / 라이선스

MIT License
MIT 라이선스

## Contributing / 기여하기

Contributions are welcome! Please feel free to submit a Pull Request.
기여는 언제나 환영합니다! Pull Request를 자유롭게 제출해주세요.

---
Perplexity로부터의 답변: pplx.ai/share
