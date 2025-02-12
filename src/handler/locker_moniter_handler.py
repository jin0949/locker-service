import asyncio
import logging
import time


class LockerMonitorHandler:
    def __init__(self, locker, supa_db):
        self.locker = locker
        self.supa_db = supa_db
        self.storage_states = {}
        self.last_full_sync = 0
        self.FULL_SYNC_INTERVAL = 60
        logging.info("Locker monitoring system initialized")

    async def initialize_states(self):
        try:
            storages = self.supa_db.get_all_storages()
            if not storages:
                logging.warning("Storage initialization failed: No storage units found")
                return False

            for storage in storages:
                current_state = self.locker.is_locked(storage['number'])
                self.storage_states[storage['id']] = {
                    'number': storage['number'],
                    'is_locked': current_state
                }
                self.supa_db.update_storage_status(storage['id'], current_state)
                logging.debug(f"Storage {storage['number']} initialized: {'Locked' if current_state else 'Unlocked'}")

            self.last_full_sync = time.time()
            logging.info("All storage units initialized successfully")
            return True
        except Exception as e:
            logging.critical(f"System initialization failed: {str(e)}")
            raise Exception(f"System initialization failed: {str(e)}")

    async def full_sync(self):
        try:
            logging.debug("Starting full system synchronization")
            storages = self.supa_db.get_all_storages()
            if not storages:
                logging.warning("Full sync failed: No storage units found")
                return

            current_ids = {storage['id'] for storage in storages}
            removed_ids = set(self.storage_states.keys()) - current_ids

            for storage_id in removed_ids:
                del self.storage_states[storage_id]
                logging.debug(f"Storage unit {storage_id} removed from monitoring")

            for storage in storages:
                current_state = self.locker.is_locked(storage['number'])
                stored_state = self.storage_states.get(storage['id'])

                if not stored_state or stored_state['is_locked'] != current_state:
                    self.storage_states[storage['id']] = {
                        'number': storage['number'],
                        'is_locked': current_state
                    }
                    self.supa_db.update_storage_status(storage['id'], current_state)
                    logging.debug(
                        f"Storage {storage['number']} state changed: {'Locked' if current_state else 'Unlocked'}")

            self.last_full_sync = time.time()
            logging.debug("Full synchronization completed")
        except Exception as e:
            logging.error(f"Full sync operation failed: {str(e)}")

    async def start(self):
        if not await self.initialize_states():
            logging.critical("System monitor initialization failed - shutting down")
            raise Exception("System monitor initialization failed - shutting down")

        logging.info("Locker monitoring system started")
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
                        logging.debug(
                            f"Storage {storage_info['number']} state change detected: {'Locked' if current_state else 'Unlocked'}")

                await asyncio.sleep(1)
            except Exception as e:
                logging.critical(f"Critical monitoring system error: {str(e)}")
                raise Exception(f"Critical monitoring system error: {str(e)}")
