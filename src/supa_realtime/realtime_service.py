import asyncio
import logging
import websockets
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
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 5  # seconds
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

    async def _cleanup_channel(self):
        """Clean up existing channel subscription"""
        if self._channel:
            try:
                await self._channel.unsubscribe()
                logging.debug("Existing channel unsubscribed")
            except Exception as e:
                logging.warning(f"Error unsubscribing channel: {str(e)}")
            finally:
                self._channel = None

    async def _cleanup_socket(self):
        """Clean up existing socket connection"""
        if self._socket:
            try:
                await self._socket.close()
                logging.debug("Existing socket closed")
            except Exception as e:
                logging.warning(f"Error closing socket: {str(e)}")
            finally:
                self._socket = None

    async def _setup_channel(self):
        try:
            # Cleanup existing channel
            await self._cleanup_channel()

            # Create and setup new channel
            self._channel = self._socket.channel("realtime:public:locker_open_requests")
            logging.info("Channel created")

            # Setup subscription
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
            await self._cleanup_channel()
            return False

    async def _connect_socket(self):
        try:
            # Cleanup existing socket
            await self._cleanup_socket()

            # Create and connect new socket
            with temporary_log_level(logging.WARNING):
                self._socket = AsyncRealtimeClient(
                    f"{self.url}/realtime/v1",
                    self.jwt,
                    auto_reconnect=False
                )
                await self._socket.connect()
            logging.debug("New socket connected")
            return True
        except Exception as e:
            logging.error(f"Socket connection failed: {str(e)}")
            await self._cleanup_socket()
            return False

    async def establish_connection(self):
        logging.info("Establishing socket connection...")
        try:
            if not await self._connect_socket():
                logging.warning("Failed to connect socket")
                return False

            logging.info("Socket connected successfully")

            if not await self._setup_channel():
                logging.warning("Failed to setup channel")
                await self._cleanup_socket()
                return False

            return True

        except Exception as e:
            logging.error(f"Connection establishment failed: {str(e)}")
            await self._cleanup_socket()
            return False

    async def start_listening(self):
        self._is_running = True
        self._reconnect_attempts = 0

        while self._is_running:
            try:
                if not self._socket or not self._socket.is_connected:
                    if self._reconnect_attempts >= self._max_reconnect_attempts:
                        raise RuntimeError("Failed to establish realtime connection after maximum retries")

                    logging.warning(
                        f"Socket disconnected, attempting to reconnect... (Attempt {self._reconnect_attempts + 1}/{self._max_reconnect_attempts})")
                    success = await self.establish_connection()

                    if not success:
                        self._reconnect_attempts += 1
                        await asyncio.sleep(self._reconnect_delay)
                        continue

                    self._reconnect_attempts = 0
                    logging.info("Successfully reconnected")

                await self._socket.listen()

            except websockets.exceptions.ConnectionClosedError:
                raise Exception("Connection closed by server")
            except Exception as e:
                if self._is_running:
                    if isinstance(e, websockets.exceptions.WebSocketException):
                        raise Exception(f"WebSocket error: {str(e)}")
                    raise RuntimeError(f"Realtime service critical failure: {str(e)}")

    async def stop_listening(self):
        self._is_running = False
        await self._cleanup_channel()
        await self._cleanup_socket()
        logging.warning("Service stopped and connection closed")

    async def test_connection(self):
        logging.info("Testing connection...")
        temp_socket = None
        try:
            with temporary_log_level(logging.WARNING):
                temp_socket = AsyncRealtimeClient(
                    f"{self.url}/realtime/v1",
                    self.jwt,
                    auto_reconnect=False
                )
                await temp_socket.connect()

            logging.info("Test connection successful")
            return True
        except Exception as e:
            logging.error(f"Test connection failed: {str(e)}")
            return False
        finally:
            if temp_socket:
                try:
                    await temp_socket.close()
                    logging.debug("Test connection closed")
                except:
                    pass
