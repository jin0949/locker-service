import logging

from src.locker.locker import Locker
from src.supa_db.supa_db import SupaDB
from src.supa_realtime.config import DATABASE_URL, JWT
from src.supa_realtime.realtime_service import RealtimeService


class LockerOpenRequestsHandler:
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