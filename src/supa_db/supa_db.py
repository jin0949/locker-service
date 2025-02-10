import logging
from supabase import create_client, Client


class SupaDB:
    def __init__(self, database_url: str, jwt: str):
        self.client: Client = create_client(database_url, jwt)

    def get_user_role(self, user_id: str) -> str:
        try:
            result = self.client.table('profiles').select('role').eq('id', user_id).execute()
            return result.data[0]['role'] if result.data else None
        except Exception as e:
            logging.error(f"Role lookup failed: {str(e)}")
            return None

    def get_storage_info(self, storage_id: str):
        try:
            result = self.client.table('storages').select('*').eq('id', storage_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"Storage lookup failed: {str(e)}")
            return None

    def get_laundry_info(self, laundry_id: str):
        try:
            result = self.client.table('laundry').select('*').eq('id', laundry_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"Laundry lookup failed: {str(e)}")
            return None

    def get_all_storages(self):
        try:
            result = self.client.table('storages').select('*').execute()
            return result.data if result.data else None
        except Exception as e:
            logging.error(f"Failed to get all storages: {str(e)}")
            return None

    def update_request_status(self, request_id: str, status: str):
        try:
            self.client.table('locker_open_requests') \
                .update({'status': status}) \
                .eq('id', request_id) \
                .execute()
            logging.info(f"Request {request_id} status updated to {status}")
        except Exception as e:
            logging.error(f"Failed to update request status: {str(e)}")

    def free_storage(self, storage_id: str):
        try:
            self.client.table('storages') \
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

    def update_storage_status(self, storage_id: str, is_locked: bool):
        try:
            status = 'closed' if is_locked else 'open'
            self.client.table('storages') \
                .update({'status': status}) \
                .eq('id', storage_id) \
                .execute()
            logging.info(f"Storage {storage_id} status updated to {status}")
        except Exception as e:
            logging.error(f"Failed to update storage status: {str(e)}")
