import asyncio
import logging
from realtime import AsyncRealtimeClient
from typing import Callable


class RealtimeService:
    def __init__(self, url: str, jwt: str):
        self.url = url
        self.jwt = jwt
        self.callback = None
        self._socket = None
        logging.info(f"RealtimeService initialized with URL: {url}")

    def set_callback(self, callback: Callable):
        self.callback = callback
        logging.info("Callback function set")

    def _callback_wrapper(self, payload):
        if self.callback:
            logging.info(f"Received payload: {payload}")
            asyncio.create_task(self.callback(payload))
        else:
            logging.warning("Callback received but no callback function is set")

    async def _setup_channel(self):
        self._channel = self._socket.channel("realtime:public:locker_open_requests")
        logging.info("Channel created")
        await self._channel.on_postgres_changes(
            event="INSERT",
            schema="public",
            table="locker_open_requests",
            callback=self._callback_wrapper
        ).subscribe()
        logging.info("Channel subscribed successfully")

    async def reconnect(self):
        logging.info("Initiating reconnection...")
        if self._socket:
            await self._socket.close()
            logging.info("Previous socket connection closed")
        await self.start_listening()

    async def start_listening(self):
        try:
            logging.info("Starting realtime service...")
            self._socket = AsyncRealtimeClient(
                f"{self.url}/realtime/v1",
                self.jwt,
                auto_reconnect=True
            )
            await self._socket.connect()
            logging.info("Socket connected successfully")

            await self._setup_channel()
            asyncio.create_task(self._monitor_connection())
            logging.info("Starting to listen for changes")
            await self._socket.listen()

        except Exception as e:
            logging.error(f"Connection error occurred: {str(e)}")
            await asyncio.sleep(5)
            logging.info("Attempting to reconnect after error")
            await self.reconnect()

    async def _monitor_connection(self):
        while True:
            if not self._socket or not self._socket.is_connected:
                logging.warning("Connection lost or socket not initialized")
                await self.reconnect()
            await asyncio.sleep(5)

    async def test_connection(self):
        logging.info("Testing connection...")
        self._socket = AsyncRealtimeClient(f"{self.url}/realtime/v1", self.jwt, auto_reconnect=True)
        await self._socket.connect()
        logging.info("Test connection successful")
        await self._socket.close()
        logging.info("Test connection closed")
