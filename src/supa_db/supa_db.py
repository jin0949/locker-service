import logging
from supabase import create_client, Client

class SupaDB:
    def __init__(self, database_url: str, jwt: str):
        self.client: Client = create_client(database_url, jwt)
        logging.info("SupaDB initialized")

    def get_user_role(self, user_id: str):
        try:
            logging.info(f"Looking up role for user: {user_id}")
            result = self.client.table('profiles').select('role').eq('id', user_id).execute()
            if result.data:
                logging.info(f"Found role for user {user_id}: {result.data[0]['role']}")
                return result.data[0]['role']
            logging.warning(f"No role found for user: {user_id}")
            return None
        except Exception as e:
            logging.error(f"Role lookup failed for user {user_id}: {str(e)}")
            return None

    def get_storage_info(self, storage_id: str):
        try:
            logging.info(f"Looking up storage info: {storage_id}")
            result = self.client.table('storages').select('*').eq('id', storage_id).execute()
            if result.data:
                logging.info(f"Found storage info for {storage_id}")
                return result.data[0]
            logging.warning(f"No storage found with id: {storage_id}")
            return None
        except Exception as e:
            logging.error(f"Storage lookup failed for {storage_id}: {str(e)}")
            return None

    def get_laundry_info(self, laundry_id: str):
        try:
            logging.info(f"Looking up laundry info: {laundry_id}")
            result = self.client.table('laundry').select('*').eq('id', laundry_id).execute()
            if result.data:
                logging.info(f"Found laundry info for {laundry_id}")
                return result.data[0]
            logging.warning(f"No laundry found with id: {laundry_id}")
            return None
        except Exception as e:
            logging.error(f"Laundry lookup failed for {laundry_id}: {str(e)}")
            return None

    def get_all_storages(self):
        try:
            logging.info("Fetching all storages")
            result = self.client.table('storages').select('*').execute()
            if result.data:
                logging.info(f"Found {len(result.data)} storages")
                return result.data
            logging.warning("No storages found")
            return None
        except Exception as e:
            logging.error(f"Failed to fetch all storages: {str(e)}")
            return None

    def update_request_status(self, request_id: str, status: str):
        try:
            logging.info(f"Updating request {request_id} status to {status}")
            self.client.table('locker_open_requests') \
                .update({'status': status}) \
                .eq('id', request_id) \
                .execute()
            logging.info(f"Successfully updated request {request_id} to {status}")
        except Exception as e:
            logging.error(f"Failed to update request {request_id} status: {str(e)}")

    def free_storage(self, storage_id: str):
        try:
            logging.info(f"Freeing storage: {storage_id}")
            self.client.table('storages') \
                .update({
                    'status': 'open',
                    'allocated_to': None,
                    'allocated_by': None,
                    'laundry_id': None
                }) \
                .eq('id', storage_id) \
                .execute()
            logging.info(f"Successfully freed storage {storage_id}")
        except Exception as e:
            logging.error(f"Failed to free storage {storage_id}: {str(e)}")

    def update_storage_status(self, storage_id: str, is_locked: bool):
        try:
            status = 'closed' if is_locked else 'open'
            logging.info(f"Updating storage {storage_id} status to {status}")
            self.client.table('storages') \
                .update({'status': status}) \
                .eq('id', storage_id) \
                .execute()
            logging.info(f"Successfully updated storage {storage_id} to {status}")
        except Exception as e:
            logging.error(f"Failed to update storage {storage_id} status: {str(e)}")
