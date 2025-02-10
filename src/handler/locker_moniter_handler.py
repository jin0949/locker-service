import asyncio
import logging
import time


class LockerMonitorHandler:
    def __init__(self, locker, supa_db, realtime_service):
        self.locker = locker
        self.supa_db = supa_db
        self.realtime_service = realtime_service
        self.storage_states = {}  # {storage_id: {'number': number, 'is_locked': bool}}
        self.last_full_sync = 0
        self.FULL_SYNC_INTERVAL = 60  # 1분 주기로 전체 동기화

    async def initialize_states(self):
        """초기 상태 동기화"""
        try:
            storages = self.supa_db.get_all_storages()
            if not storages:
                return False

            for storage in storages:
                current_state = self.locker.is_locked(storage['number'])
                self.storage_states[storage['id']] = {
                    'number': storage['number'],
                    'is_locked': current_state
                }
                self.supa_db.update_storage_status(storage['id'], current_state)

            self.last_full_sync = time.time()
            return True
        except Exception as e:
            logging.error(f"Failed to initialize states: {str(e)}")
            return False

    async def full_sync(self):
        """전체 상태 동기화"""
        try:
            storages = self.supa_db.get_all_storages()
            if not storages:
                return

            # 삭제된 storage 제거
            current_ids = {storage['id'] for storage in storages}
            removed_ids = set(self.storage_states.keys()) - current_ids
            for storage_id in removed_ids:
                del self.storage_states[storage_id]

            # 모든 storage 상태 확인 및 업데이트
            for storage in storages:
                current_state = self.locker.is_locked(storage['number'])
                stored_state = self.storage_states.get(storage['id'])

                if not stored_state or stored_state['is_locked'] != current_state:
                    self.storage_states[storage['id']] = {
                        'number': storage['number'],
                        'is_locked': current_state
                    }
                    self.supa_db.update_storage_status(storage['id'], current_state)

            self.last_full_sync = time.time()
        except Exception as e:
            logging.error(f"Error in full sync: {str(e)}")

    async def monitor_locker_states(self):
        """상태 모니터링 메인 루프"""
        if not await self.initialize_states():
            logging.error("Failed to initialize locker states")
            return

        while True:
            try:
                # 1분마다 전체 동기화 수행
                current_time = time.time()
                if current_time - self.last_full_sync >= self.FULL_SYNC_INTERVAL:
                    await self.full_sync()

                # 현재 저장된 모든 사물함 상태 확인
                for storage_id, storage_info in self.storage_states.items():
                    current_state = self.locker.is_locked(storage_info['number'])

                    if current_state != storage_info['is_locked']:
                        self.storage_states[storage_id]['is_locked'] = current_state
                        self.supa_db.update_storage_status(storage_id, current_state)

                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Error in monitor_locker_states: {str(e)}")
                await asyncio.sleep(5)
