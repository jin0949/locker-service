import asyncio
import logging

from setproctitle import setproctitle

from src.handler.locker_moniter_handler import LockerMonitorHandler
from src.handler.locker_open_requests_handler import LockerOpenRequestsHandler
from src.locker.locker import Locker


async def main():
    setproctitle("locker-service")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Single Locker instance
        port = '/dev/ttyUSB0'
        locker = Locker(port)

        # Initialize handlers with shared locker
        laundry_handler = LockerOpenRequestsHandler(locker=locker)
        locker_monitor = LockerMonitorHandler(locker=locker)

        await asyncio.gather(
            laundry_handler.start(),
            locker_monitor.monitor_locker_states(),
        )
    except Exception as e:
        logging.error(f"Main process error: {str(e)}")
    finally:
        if locker:
            locker.close()


if __name__ == "__main__":
    asyncio.run(main())
