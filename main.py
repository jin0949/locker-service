import asyncio
import logging
import os
import argparse
import sys

from setproctitle import setproctitle
from dotenv import load_dotenv

from src.handler.locker_moniter_handler import LockerMonitorHandler
from src.handler.locker_open_requests_handler import LockerOpenRequestsHandler
from src.locker.locker import Locker
from src.supa_db.supa_db import SupaDB
from src.supa_realtime.realtime_service import RealtimeService
from src.utils.logger import setup_logger

SERVICE_NAME = "locker-service"


def parse_arguments():
    parser = argparse.ArgumentParser(description='Locker Service')
    # parser.add_argument('--port', default='COM6', help='Serial port for locker connection')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port for locker connection')
    parser.add_argument('--log-level',
                        default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    parser.add_argument('--log-dir',
                        default='logs',
                        help='Directory for log files')
    return parser.parse_args()


async def main():
    try:
        args = parse_arguments()

        setup_logger(args.log_dir, logging.getLevelName(args.log_level))
        setproctitle(SERVICE_NAME)
        load_dotenv()

        database_url = os.getenv('DATABASE_URL')
        jwt = os.getenv('JWT')

        if not all([database_url, jwt]):
            raise Exception("Required environment variables are missing")

        logging.info(f"Starting {SERVICE_NAME} with port {args.port}")

        locker = Locker(args.port)
        supa_db = SupaDB(database_url, jwt)
        realtime_service = RealtimeService(database_url, jwt)

        handlers = [
            LockerOpenRequestsHandler(locker, supa_db, realtime_service).start(),
            LockerMonitorHandler(locker, supa_db).start(),
        ]

        await asyncio.gather(*handlers)

    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Service shutting down gracefully...")
    except Exception as e:
        logging.critical(f"Service error: {str(e)}")
        sys.exit(1)
    finally:
        if 'locker' in locals():
            locker.close()


if __name__ == "__main__":
    asyncio.run(main())
