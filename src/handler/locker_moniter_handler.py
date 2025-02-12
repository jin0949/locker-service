import asyncio
import logging
import time


class LockerMonitorHandler:
    def __init__(self, locker, supa_db, realtime_service):
        self.locker = locker
        self.supa_db = supa_db
        self.realtime_service = realtime_service
        self.storage_states = {}
        self.last_full_sync = 0
        self.FULL_SYNC_INTERVAL = 60
        logging.info("LockerMonitorHandler initialized")

    async def initialize_states(self):
        try:
            storages = self.supa_db.get_all_storages()
            if not storages:
                logging.warning("No storages found during initialization")
                return False

            for storage in storages:
                current_state = self.locker.is_locked(storage['number'])
                self.storage_states[storage['id']] = {
                    'number': storage['number'],
                    'is_locked': current_state
                }
                self.supa_db.update_storage_status(storage['id'], current_state)
                logging.debug(
                    f"Initialized storage {storage['id']}: locker {storage['number']} is {'locked' if current_state else 'unlocked'}")

            self.last_full_sync = time.time()
            logging.info("Storage states initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Storage states initialization failed: {str(e)}")
            return False

    async def full_sync(self):
        try:
            logging.info("Starting full sync")
            storages = self.supa_db.get_all_storages()
            if not storages:
                logging.warning("No storages found during full sync")
                return

            current_ids = {storage['id'] for storage in storages}
            removed_ids = set(self.storage_states.keys()) - current_ids

            for storage_id in removed_ids:
                del self.storage_states[storage_id]
                logging.info(f"Removed storage {storage_id} from monitoring")

            for storage in storages:
                current_state = self.locker.is_locked(storage['number'])
                stored_state = self.storage_states.get(storage['id'])

                if not stored_state or stored_state['is_locked'] != current_state:
                    self.storage_states[storage['id']] = {
                        'number': storage['number'],
                        'is_locked': current_state
                    }
                    self.supa_db.update_storage_status(storage['id'], current_state)
                    logging.info(
                        f"Updated storage {storage['id']}: locker {storage['number']} is {'locked' if current_state else 'unlocked'}")

            self.last_full_sync = time.time()
            logging.info("Full sync completed")
        except Exception as e:
            logging.error(f"Full sync failed: {str(e)}")

    async def monitor_locker_states(self):
        if not await self.initialize_states():
            logging.error("Monitor initialization failed")
            return

        logging.info("Starting locker state monitoring")
        while True:
            try:
                current_time = time.time()
                if current_time - self.last_full_sync >= self.FULL_SYNC_INTERVAL:
                    await self.full_sync()

                for storage_id, storage_info in self.storage_states.items():
                    current_state = self.locker.is_locked(storage_info['number'])

                    if current_state != storage_info['is_locked']:
                        self.storage_states[storage_id]['is_locked'] = current_state
                        self.supa_db.update_storage_status(storage_id, current_state)
                        logging.info(
                            f"State change detected - Storage {storage_id}: locker {storage_info['number']} is {'locked' if current_state else 'unlocked'}")

                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(5)
