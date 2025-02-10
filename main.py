import asyncio
import logging
import time

from src.locker.locker import Locker
from src.supa_db.supa_db import SupaDB
from src.supa_realtime.config import DATABASE_URL, JWT
from src.supa_realtime.realtime_service import RealtimeService


class LaundryHandler:
    def __init__(self):
        self.supa_api = SupaDB()
        self.service = RealtimeService(DATABASE_URL, JWT, self.handle_change)
        self.locker = Locker("COM6")

    async def handle_change(self, payload):
        try:
            logging.info(f"Database change detected: {payload}")
            record = payload['data']['record']

            # 1. Get essential data
            request_id = record['id']
            storage_id = record['storage_id']
            requested_by = record['requested_by']

            # 2. Get storage info
            storage = self.supa_api.get_storage_info(storage_id)
            if not storage:
                await self.update_request_status(request_id, 'failed')
                logging.error(f"Storage {storage_id} not found")
                return

            # 3. Get user role
            user_role = self.supa_api.get_user_role(requested_by)
            if not user_role:
                await self.update_request_status(request_id, 'failed')
                logging.error(f"User role not found for {requested_by}")
                return

            # 4. Handle manager/deliver case
            if user_role in ['deliver', 'manager']:
                if await self.open_locker(storage['number']):
                    await self.update_request_status(request_id, 'success')
                    await self.free_storage(storage_id)
                    return
                await self.update_request_status(request_id, 'failed')
                return

            # 5. Handle regular user case
            if not storage['laundry_id']:
                await self.update_request_status(request_id, 'failed')
                logging.error(f"No laundry associated with storage {storage_id}")
                return

            # 6. Check payment status
            laundry = self.supa_api.get_laundry_info(storage['laundry_id'])
            if not laundry or not laundry['paid']:
                await self.update_request_status(request_id, 'reject')
                logging.info(f"Payment required for laundry {storage['laundry_id']}")
                return

            # 7. Open locker for paid user
            if await self.open_locker(storage['number']):
                await self.update_request_status(request_id, 'success')
                await self.free_storage(storage_id)
                return
            await self.update_request_status(request_id, 'failed')

        except Exception as e:
            logging.error(f"Error in handle_change: {str(e)}")
            await self.update_request_status(request_id, 'failed')

    async def free_storage(self, storage_id: str):
        try:
            self.supa_api.client.table('storages') \
                .update({
                    'status': 'open',
                    'allocated_to': None,
                    'allocated_by': None,
                    'laundry_id': None
                }) \
                .eq('id', storage_id) \
                .execute()
            logging.info(f"Storage {storage_id} freed successfully")
        except Exception as e:
            logging.error(f"Failed to free storage {storage_id}: {str(e)}")

    async def open_locker(self, number: int) -> bool:
        try:
            return self.locker.open(number)
        except Exception as e:
            logging.error(f"Failed to open locker {number}: {str(e)}")
            return False

    async def update_request_status(self, request_id: str, status: str):
        try:
            self.supa_api.client.table('locker_open_requests') \
                .update({'status': status}) \
                .eq('id', request_id) \
                .execute()
            logging.info(f"Request {request_id} status updated to {status}")
        except Exception as e:
            logging.error(f"Failed to update request status: {str(e)}")

    async def start(self):
        await self.service.start_listening()


class LockerMonitorHandler:
    def __init__(self, locker: Locker):
        self.locker = locker
        self.supa_api = SupaDB()
        self.storage_states = {}  # {storage_id: {'number': number, 'is_locked': bool}}
        self.last_full_sync = 0
        self.FULL_SYNC_INTERVAL = 60  # 1분 주기로 전체 동기화

    async def initialize_states(self):
        """초기 상태 동기화"""
        try:
            storages = self.supa_api.get_all_storages()
            if not storages:
                return False

            for storage in storages:
                current_state = self.locker.is_locked(storage['number'])
                self.storage_states[storage['id']] = {
                    'number': storage['number'],
                    'is_locked': current_state
                }
                self.supa_api.update_storage_status(storage['id'], current_state)

            self.last_full_sync = time.time()
            return True
        except Exception as e:
            logging.error(f"Failed to initialize states: {str(e)}")
            return False

    async def full_sync(self):
        """전체 상태 동기화"""
        try:
            storages = self.supa_api.get_all_storages()
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
                    self.supa_api.update_storage_status(storage['id'], current_state)

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
                        self.supa_api.update_storage_status(storage_id, current_state)

                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Error in monitor_locker_states: {str(e)}")
                await asyncio.sleep(5)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Initialize handlers
        laundry_handler = LaundryHandler()
        locker_monitor = LockerMonitorHandler(laundry_handler.locker)

        # Run both handlers concurrently
        await asyncio.gather(
            laundry_handler.start(),
            locker_monitor.monitor_locker_states(),
        )
    except Exception as e:
        logging.error(f"Main process error: {str(e)}")
    finally:
        # Cleanup
        if hasattr(laundry_handler, 'locker'):
            laundry_handler.locker.close()


if __name__ == "__main__":
    asyncio.run(main())
