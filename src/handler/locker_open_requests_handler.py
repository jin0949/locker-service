import logging


class LockerOpenRequestsHandler:
    def __init__(self, locker, supa_db, realtime_service):
        self.locker = locker
        self.supa_db = supa_db
        self.realtime_service = realtime_service
        self.realtime_service.set_callback(self.handle_change)
        logging.info("LockerOpenRequestsHandler initialized successfully")

    async def handle_change(self, payload):
        try:
            logging.debug(f"New locker open request received: {payload}")
            record = payload['data']['record']
            request_id = record['id']
            storage_id = record['storage_id']
            requested_by = record['requested_by']

            storage = self.supa_db.get_storage_info(storage_id)
            if not storage:
                logging.error(f"Storage unit not found in database: {storage_id}")
                await self.update_request_status(request_id, 'failed')
                return

            user_role = self.supa_db.get_user_role(requested_by)
            if not user_role:
                logging.error(f"User role not found for user: {requested_by}")
                await self.update_request_status(request_id, 'failed')
                return

            if user_role in ['deliver', 'manager']:
                logging.debug(f"Processing {user_role} request for storage unit {storage_id}")
                if await self.open_locker(storage['number']):
                    await self.update_request_status(request_id, 'success')
                    await self.free_storage(storage_id)
                    return
                await self.update_request_status(request_id, 'failed')
                return

            if not storage['laundry_id']:
                logging.error(f"No laundry associated with storage unit: {storage_id}")
                await self.update_request_status(request_id, 'failed')
                return

            laundry = self.supa_db.get_laundry_info(storage['laundry_id'])
            if not laundry or not laundry['paid']:
                logging.debug(f"Payment required for laundry: {storage['laundry_id']}")
                await self.update_request_status(request_id, 'reject')
                return

            logging.debug(f"Processing paid user request for storage unit {storage_id}")
            if await self.open_locker(storage['number']):
                await self.update_request_status(request_id, 'success')
                await self.free_storage(storage_id)
                return
            await self.update_request_status(request_id, 'failed')

        except Exception as e:
            logging.error(f"Request processing failed: {str(e)}")
            await self.update_request_status(request_id, 'failed')

    async def free_storage(self, storage_id: str):
        try:
            self.supa_db.free_storage(storage_id)
            logging.debug(f"Storage unit freed successfully: {storage_id}")
        except Exception as e:
            logging.error(f"Failed to free storage unit {storage_id}: {str(e)}")

    async def open_locker(self, number: int) -> bool:
        try:
            result = self.locker.open(number)
            if result:
                logging.debug(f"Locker {number} opened successfully")
            else:
                logging.debug(f"Failed to open locker {number}")
            return result
        except Exception as e:
            logging.error(f"Error occurred while opening locker {number}: {str(e)}")
            return False

    async def update_request_status(self, request_id: str, status: str):
        try:
            self.supa_db.update_request_status(request_id, status)
            logging.debug(f"Request {request_id} status updated to: {status}")
        except Exception as e:
            logging.error(f"Failed to update status for request {request_id}: {str(e)}")

    async def start(self):
        logging.info("Starting LockerOpenRequestsHandler")
        try:
            await self.realtime_service.start_listening()
        except Exception as e:
            raise Exception(f"Failed to start LockerOpenRequestsHandler: {str(e)}")

