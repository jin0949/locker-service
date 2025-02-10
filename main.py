import asyncio
import logging

from src.handler.locker_moniter_handler import LockerMonitorHandler
from src.handler.locker_open_requests_handler import LockerOpenRequestsHandler


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Initialize handlers
        laundry_handler = LockerOpenRequestsHandler()
        locker_monitor = LockerMonitorHandler(laundry_handler.locker)

        # Run both handlers concurrently
        await asyncio.gather(
            laundry_handler.start(),
            locker_monitor.monitor_locker_states(),
        )
    except Exception as e:
        logging.error(f"Main process error: {str(e)}")
    finally:
        # Cleanup
        if hasattr(laundry_handler, 'locker'):
            laundry_handler.locker.close()


if __name__ == "__main__":
    asyncio.run(main())
