import logging

from supabase import create_client
from supa_realtime.config import DATABASE_URL, JWT


class SupaDB:
    def __init__(self):
        self.client = create_client(DATABASE_URL, JWT)

    def get_user_role(self, user_id: str) -> str:
        try:
            result = self.client.table('profiles') \
                .select('role') \
                .eq('id', user_id) \
                .execute()
            return result.data[0]['role'] if result.data else None
        except Exception as e:
            logging.error(f"Role lookup failed: {str(e)}")
            return None

    def get_storage_info(self, storage_id: str):
        try:
            result = self.client.table('storages') \
                .select('*') \
                .eq('id', storage_id) \
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"Storage lookup failed: {str(e)}")
            return None

    def get_laundry_info(self, laundry_id: str):
        try:
            result = self.client.table('laundry') \
                .select('*') \
                .eq('id', laundry_id) \
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"Laundry lookup failed: {str(e)}")
            return None