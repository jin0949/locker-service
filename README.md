# Laundry Management System with KR-CU16 Locker Control
# 세탁물 관리 시스템 (KR-CU16 사물함 제어 포함)

This project implements a comprehensive laundry management system that integrates the KR-CU16 locker control system with a real-time database for handling laundry service operations.
이 프로젝트는 KR-CU16 사물함 제어 시스템과 실시간 데이터베이스를 통합하여 세탁 서비스 운영을 처리하는 종합적인 세탁물 관리 시스템을 구현합니다.

## System Architecture / 시스템 구조

- **Hardware Control**: KR-CU16 locker system via RS485-USB
- **Database**: Supabase (PostgreSQL)
- **Real-time Updates**: Supabase Realtime
- **Background Monitoring**: Asynchronous state monitoring system
- **하드웨어 제어**: RS485-USB를 통한 KR-CU16 사물함 시스템
- **데이터베이스**: Supabase (PostgreSQL)
- **실시간 업데이트**: Supabase Realtime
- **백그라운드 모니터링**: 비동기 상태 모니터링 시스템

## Core Features / 주요 기능

### 1. Role-based Access Control / 역할 기반 접근 제어
- Manager/Deliver: Full access to lockers
- Users: Access based on payment status
- 관리자/배송원: 사물함 전체 접근 가능
- 일반 사용자: 결제 상태에 따른 접근

### 2. Automated Locker Management / 자동화된 사물함 관리
- Real-time locker status monitoring
- Automatic storage allocation/deallocation
- Memory-optimized state tracking
- Periodic full synchronization
- 실시간 사물함 상태 모니터링
- 자동 저장공간 할당/해제
- 메모리 최적화된 상태 추적
- 주기적 전체 동기화

### 3. Payment Integration / 결제 연동
- Payment verification for user access
- Automated access control based on payment status
- 사용자 접근을 위한 결제 확인
- 결제 상태에 따른 자동 접근 제어

## Main Process Flow / 주요 처리 흐름

### Request Handler / 요청 처리
1. Locker open request detection
2. User role & permission verification
3. Payment status check (for regular users)
4. Locker control execution
5. Storage status update

### State Monitor / 상태 모니터링
1. Initial state synchronization
2. Real-time state change detection
3. Memory-based state tracking
4. Periodic full synchronization (every 60s)
5. Differential updates to database

## Technical Requirements / 기술 요구사항

- Python 3.7+
- KR-CU16 Locker System
- Supabase Account
- RS485-USB Converter
- 12V 2.5A Power Supply

## System Components / 시스템 구성요소

### LaundryHandler
- Handles real-time open requests
- Manages user permissions
- Controls locker operations
- 실시간 열기 요청 처리
- 사용자 권한 관리
- 사물함 작동 제어

### LockerMonitorHandler
- Monitors physical locker states
- Maintains in-memory state cache
- Performs periodic synchronization
- 물리적 사물함 상태 모니터링
- 메모리 내 상태 캐시 관리
- 주기적 동기화 수행

---
