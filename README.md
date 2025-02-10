# Laundry Management System with KR-CU16 Locker Control
# 세탁물 관리 시스템 (KR-CU16 사물함 제어 포함)

This project implements a comprehensive laundry management system that integrates the KR-CU16 locker control system with a real-time database for handling laundry service operations.
이 프로젝트는 KR-CU16 사물함 제어 시스템과 실시간 데이터베이스를 통합하여 세탁 서비스 운영을 처리하는 종합적인 세탁물 관리 시스템을 구현합니다.

## System Architecture / 시스템 구조

- **Hardware Control**: KR-CU16 locker system via RS485-USB
- **Database**: Supabase (PostgreSQL)
- **Real-time Updates**: Supabase Realtime
- **하드웨어 제어**: RS485-USB를 통한 KR-CU16 사물함 시스템
- **데이터베이스**: Supabase (PostgreSQL)
- **실시간 업데이트**: Supabase Realtime

## Core Features / 주요 기능

### 1. Role-based Access Control / 역할 기반 접근 제어
- Manager/Deliver: Full access to lockers
- Users: Access based on payment status
- 관리자/배송원: 사물함 전체 접근 가능
- 일반 사용자: 결제 상태에 따른 접근

### 2. Automated Locker Management / 자동화된 사물함 관리
- Real-time locker status monitoring
- Automatic storage allocation/deallocation
- 실시간 사물함 상태 모니터링
- 자동 저장공간 할당/해제

### 3. Payment Integration / 결제 연동
- Payment verification for user access
- Automated access control based on payment status
- 사용자 접근을 위한 결제 확인
- 결제 상태에 따른 자동 접근 제어

## Main Process Flow / 주요 처리 흐름

1. Locker open request detection
2. User role & permission verification
3. Payment status check (for regular users)
4. Locker control execution
5. Storage status update

1. 사물함 열기 요청 감지
2. 사용자 역할 및 권한 확인
3. 결제 상태 확인 (일반 사용자)
4. 사물함 제어 실행
5. 저장공간 상태 업데이트

## Technical Requirements / 기술 요구사항

- Python 3.7+
- KR-CU16 Locker System
- Supabase Account
- RS485-USB Converter
- 12V 2.5A Power Supply
---
