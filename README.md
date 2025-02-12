# Locker Service
물품 보관함 서비스

## Overview
시스템 개요

This service controls and monitors a smart locker system with real-time communication capabilities.
스마트 물품 보관함 시스템을 실시간으로 제어하고 모니터링하는 서비스입니다.

## Key Features
주요 기능

- Real-time locker status monitoring
- 실시간 보관함 상태 모니터링

- Processing instant open requests
- 즉각적인 열림 요청 처리

- Supabase database integration
- Supabase 데이터베이스 연동

- Real-time event handling
- 실시간 이벤트 처리

## Requirements
필수 요구사항

- Python 3.8 or higher
- Python 3.8 이상

- Serial-compatible locker hardware
- 시리얼 통신 가능한 보관함 하드웨어

- Supabase account and project
- Supabase 계정 및 프로젝트

## Setup
설정 방법

1. Create .env file:
1. .env 파일 생성:
```
DATABASE_URL=your_supabase_url
JWT=your_supabase_jwt
```

2. Install required packages:
2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## Running the Service
서비스 실행

Basic execution:
기본 실행:
```bash
python main.py
```

Run with options:
옵션 지정 실행:
```bash
python main.py --port /dev/ttyUSB0 --log-level INFO --log-dir logs
```

## Command Options
실행 옵션

- `--port`: Serial port designation (default: /dev/ttyUSB0)
- `--port`: 시리얼 포트 지정 (기본값: /dev/ttyUSB0)

- `--log-level`: Set logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `--log-level`: 로깅 레벨 설정 (DEBUG/INFO/WARNING/ERROR/CRITICAL)

- `--log-dir`: Log file directory
- `--log-dir`: 로그 파일 저장 경로

## Logging Levels
로깅 레벨

- INFO: Service status changes
- INFO: 서비스 상태 변경사항

- WARNING: Reconnection attempts and warnings
- WARNING: 재연결 시도 및 경고상황

- ERROR: Error situations
- ERROR: 오류 상황

- DEBUG: Detailed debugging information
- DEBUG: 상세 디버깅 정보

## Important Notes
주의사항

- Must configure .env file before running
- 실행 전 반드시 .env 파일 설정 필요

- Verify correct serial port configuration
- 올바른 시리얼 포트 설정 확인

- Check hardware connection status
- 하드웨어 연결 상태 확인

## Error Handling
에러 처리

- Service won't start if environment variables are missing
- 환경 변수 미설정 시 서비스 시작 불가

- Logs error on hardware connection failure
- 하드웨어 연결 실패 시 에러 로그 기록

- Automatic retry on realtime service connection failure
- 실시간 서비스 연결 실패 시 자동 재시도

---