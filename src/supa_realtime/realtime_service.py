import asyncio
import logging
from realtime import AsyncRealtimeClient
from typing import Callable

from src.utils.suppress_log import temporary_log_level


class RealtimeService:
    def __init__(self, url: str, jwt: str):
        self.url = url
        self.jwt = jwt
        self.callback = None
        self._socket = None
        self._channel = None
        self._is_running = False
        logging.info(f"RealtimeService initialized with URL: {url}")

    def set_callback(self, callback: Callable):
        self.callback = callback
        logging.debug("Callback function set")

    def _callback_wrapper(self, payload):
        if self.callback:
            logging.debug(f"Received payload: {payload}")
            asyncio.create_task(self.callback(payload))
        else:
            logging.warning("Callback received but no callback function is set")

    async def _setup_channel(self):
        try:
            self._channel = self._socket.channel("realtime:public:locker_open_requests")
            logging.info("Channel created")

            await self._channel.on_postgres_changes(
                event="INSERT",
                schema="public",
                table="locker_open_requests",
                callback=self._callback_wrapper
            ).subscribe()

            logging.info("Channel subscribed successfully")
            return True
        except Exception as e:
            logging.error(f"Channel setup failed: {str(e)}")
            return False

    async def _connect_socket(self):
        try:
            with temporary_log_level(logging.WARNING):
                self._socket = AsyncRealtimeClient(
                    f"{self.url}/realtime/v1",
                    self.jwt,
                    auto_reconnect=False
                )
                await self._socket.connect()
            return True
        except Exception as e:
            logging.error(f"Socket connection failed: {str(e)}")
            return False

    async def establish_connection(self):
        logging.info("Establishing socket connection...")
        try:
            if self._socket:
                await self._socket.close()
                logging.info("Previous socket connection closed")

            if not await self._connect_socket():
                logging.warning("Failed to connect socket")
                return False

            logging.info("Socket connected successfully")

            if await self._setup_channel():
                return True
            return False

        except Exception as e:
            logging.error(f"Connection establishment failed: {str(e)}")
            return False

    async def start_listening(self):
        self._is_running = True
        retries = 0
        max_retries = 3

        while self._is_running:
            try:
                if not self._socket or not self._socket.is_connected:
                    logging.warning("Socket disconnected, attempting to reconnect...")
                    success = await self.establish_connection()
                    if not success:
                        retries += 1
                        if retries >= max_retries:
                            raise RuntimeError("Failed to establish realtime connection after maximum retries")
                        await asyncio.sleep(5)
                        continue
                    retries = 0
                    logging.info("Successfully reconnected")
                await self._socket.listen()

            except Exception as e:
                logging.critical(f"Fatal realtime connection error: {str(e)}")
                raise RuntimeError(f"Realtime service critical failure: {str(e)}")

    async def stop_listening(self):
        self._is_running = False
        if self._socket:
            await self._socket.close()
            logging.info("Service stopped and connection closed")

    async def test_connection(self):
        logging.info("Testing connection...")
        try:
            with temporary_log_level(logging.WARNING):
                temp_socket = AsyncRealtimeClient(
                    f"{self.url}/realtime/v1",
                    self.jwt,
                    auto_reconnect=False
                )
                await temp_socket.connect()

            logging.info("Test connection successful")
            await temp_socket.close()
            logging.debug("Test connection closed")
            return True
        except Exception as e:
            logging.error(f"Test connection failed: {str(e)}")
            return False
