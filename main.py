import asyncio
import os
from setproctitle import setproctitle
from dotenv import load_dotenv

from src.handler.locker_moniter_handler import LockerMonitorHandler
from src.handler.locker_open_requests_handler import LockerOpenRequestsHandler
from src.locker.locker import Locker
from src.supa_db.supa_db import SupaDB
from src.supa_realtime.realtime_service import RealtimeService
from src.utils.logger import setup_logger

# User configurations
SERIAL_PORT = '/dev/ttyUSB0'
SERVICE_NAME = "locker-service"

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
JWT = os.getenv('JWT')


async def main():
    setproctitle(SERVICE_NAME)
    logger = setup_logger()

    try:
        # Initialize base components
        locker = Locker(SERIAL_PORT)
        supa_db = SupaDB(DATABASE_URL, JWT)

        # Initialize realtime services
        realtime_service = RealtimeService(DATABASE_URL, JWT)

        # Initialize handlers with dependencies
        open_requests_handler = LockerOpenRequestsHandler(
            locker=locker,
            supa_db=supa_db,
            realtime_service=realtime_service
        )

        monitor_handler = LockerMonitorHandler(
            locker=locker,
            supa_db=supa_db,
            realtime_service=realtime_service
        )

        await asyncio.gather(
            open_requests_handler.start(),
            monitor_handler.monitor_locker_states(),
        )
    except Exception as e:
        logger.error(f"CRITICAL: Main process error: {str(e)}")
    finally:
        if locker:
            locker.close()


if __name__ == "__main__":
    asyncio.run(main())
