import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from setproctitle import setproctitle

from src.handler.locker_moniter_handler import LockerMonitorHandler
from src.handler.locker_open_requests_handler import LockerOpenRequestsHandler
from src.locker.locker import Locker
from src.supa_db.supa_db import SupaDB
from src.supa_realtime.realtime_service import RealtimeService
from src.supa_realtime.config import DATABASE_URL, JWT


def setup_logger():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'locker-service.log')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


async def main():
    setproctitle("locker-service")
    setup_logger()

    try:
        # Initialize base components
        port = '/dev/ttyUSB0'
        locker = Locker(port)
        supa_db = SupaDB(DATABASE_URL, JWT)

        # Initialize realtime services
        open_requests_service = RealtimeService(DATABASE_URL, JWT)
        monitor_service = RealtimeService(DATABASE_URL, JWT)

        # Initialize handlers with dependencies
        open_requests_handler = LockerOpenRequestsHandler(
            locker=locker,
            supa_db=supa_db,
            realtime_service=open_requests_service
        )

        monitor_handler = LockerMonitorHandler(
            locker=locker,
            supa_db=supa_db,
            realtime_service=monitor_service
        )

        await asyncio.gather(
            open_requests_handler.start(),
            monitor_handler.monitor_locker_states(),
        )
    except Exception as e:
        logging.error(f"Main process error: {str(e)}")
    finally:
        if locker:
            locker.close()


if __name__ == "__main__":
    asyncio.run(main())
