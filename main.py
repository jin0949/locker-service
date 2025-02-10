import asyncio
import logging
import json

from src.locker import Locker
from supa_db.supa_db import SupaDB
from supa_realtime.config import DATABASE_URL, JWT
from supa_realtime.realtime_service import RealtimeService


class LaundryHandler:
    def __init__(self):
        self.supa_api = SupaDB()
        self.service = RealtimeService(DATABASE_URL, JWT, self.handle_change)
        self.locker = Locker("/dev/ttyxx")

    async def handle_change(self, payload):
        logging.info(f"Database change detected: {payload}")
        record = payload['data']['record']
        '''
        순서가 대충
        payload에 오는 row에 stoarge id가 포함되서오는데 일단 누가 요청했는지 
        
        그럼 payload 에 바로 누가 신청했는지 req id 가 있으니
        해당 id로 profile table에 role 조회후 해당 role에 따라 분기가 나누어짐
        
        role user:
        유저는 결제가 완료가 되어야지만 자신의 사물함을 열수있음.
        그러면 해당 storage의 laundry id로 조회해서
        해당 세탁 건이 결제가 되었다. 그러면 open으로 바꾸고 열림 로직 실행시키고,
        안되었다 하면 req를 reject으로 바꾸고 안열리게 하면됨.
        
        role deliver or manager:
        그냥 열어줌
        '''

    async def start(self):
        await self.service.start_listening()


async def main():
    logging.basicConfig(level=logging.INFO)
    handler = LaundryHandler()
    await handler.start()


if __name__ == "__main__":
    asyncio.run(main())
