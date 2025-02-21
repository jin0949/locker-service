# Locker Service with Printer Integration
물품 보관함 프린터 통합 서비스

## Overview
시스템 개요

A smart locker management service with integrated label printing capabilities, featuring real-time monitoring and control.
실시간 모니터링 및 제어가 가능한 라벨 프린팅 기능이 통합된 스마트 보관함 관리 서비스입니다.

## Key Features
주요 기능

- Real-time locker status monitoring and control
- 실시간 보관함 상태 모니터링 및 제어

- Automated label printing system
- 자동화된 라벨 프린팅 시스템

- Supabase database integration
- Supabase 데이터베이스 연동

- Real-time event processing
- 실시간 이벤트 처리

## Requirements
필수 요구사항

- Python 3.11
- Python 3.11

- Serial-compatible locker hardware
- 시리얼 통신 가능한 보관함 하드웨어

- Niimbot thermal printer
- Niimbot 열전사 프린터

- Supabase account and project
- Supabase 계정 및 프로젝트

## Hardware Setup
하드웨어 설정

### Locker
보관함
- Serial communication port
- 시리얼 통신 포트

### Printer
프린터
- Bluetooth connectivity
- 블루투스 연결
- Label paper installed
- 라벨 용지 설치

## Software Setup
소프트웨어 설정

1. Create .env file:
1. .env 파일 생성:
```
DATABASE_URL=your_supabase_url
JWT=your_supabase_jwt
```

2. Install dependencies:
2. 의존성 패키지 설치:
```bash
pip install -r requirements.txt
```

## Running
실행 방법

Basic execution:
기본 실행:
```bash
python main.py
```

With options:
옵션 지정:
```bash
python main.py --port COM6 --log-level INFO --log-dir logs
```

## Command Options
실행 옵션

- `--port`: Serial port (default: COM6)
- `--port`: 시리얼 포트 (기본값: COM6)

- `--log-level`: Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `--log-level`: 로깅 레벨 (DEBUG/INFO/WARNING/ERROR/CRITICAL)

- `--log-dir`: Log directory path
- `--log-dir`: 로그 저장 경로

## Logging System
로깅 시스템

### Levels
레벨
- INFO: Operation status
- INFO: 작업 상태

- WARNING: Non-critical issues
- WARNING: 경미한 문제

- ERROR: Critical problems
- ERROR: 심각한 문제

- DEBUG: Detailed information
- DEBUG: 상세 정보

## Error Handling
에러 처리

### Printer
프린터
- Connection monitoring
- 연결 상태 모니터링

- Print job management
- 프린트 작업 관리

- Status checks
- 상태 확인

### System
시스템
- Environment validation
- 환경 변수 검증

- Graceful shutdown
- 정상 종료 처리

- Auto-reconnection
- 자동 재연결

## Important Notes
주의사항

- Configure .env before running
- 실행 전 .env 설정 필수

- Check printer status regularly
- 프린터 상태 정기 점검

- Monitor paper supply
- 용지 잔량 확인

- Verify connections
- 연결 상태 확인

---

For support: Contact system administrator
기술 지원: 시스템 관리자에게 문의

---
Perplexity로부터의 답변: pplx.ai/share