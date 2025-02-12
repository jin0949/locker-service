import logging
import os
import colorlog
import asyncio
from logging.handlers import TimedRotatingFileHandler
from queue import Queue
import atexit

class AsyncBufferedTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backup_count=0, encoding=None,
                 buffer_size=1000, flush_interval=300):
        super().__init__(filename, when, interval, backup_count, encoding=encoding)
        self.queue = Queue()
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self._stop_event = asyncio.Event()
        self._flush_task = None

    def emit(self, record):
        if not self._stop_event.is_set():
            self.queue.put(record)
            if self.queue.qsize() >= self.buffer_size:
                self.flush_buffer()

    def flush_buffer(self):
        while not self.queue.empty():
            record = self.queue.get()
            super().emit(record)
        self.flush()

    async def periodic_flush(self):
        while not self._stop_event.is_set():
            self.flush_buffer()
            try:
                await asyncio.sleep(self.flush_interval)
            except asyncio.CancelledError:
                break
        self.flush_buffer()

    def close(self):
        self._stop_event.set()
        self.flush_buffer()
        super().close()

def cleanup_logger():
    for handler in logging.getLogger().handlers[:]:
        try:
            handler.close()
        except:
            pass
        logging.getLogger().removeHandler(handler)

def setup_logger(log_dir='logs', log_level=logging.INFO):
    cleanup_logger()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    debug_handler = AsyncBufferedTimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'debug.log'),
        when='midnight',
        interval=1,
        backup_count=1,
        encoding='utf-8',
        buffer_size=1000,
        flush_interval=300
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    debug_handler.setFormatter(debug_formatter)
    debug_handler.addFilter(lambda record: record.levelno == logging.DEBUG)
    logging.getLogger().addHandler(debug_handler)

    general_handler = AsyncBufferedTimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'service.log'),
        when='midnight',
        interval=1,
        backup_count=1,
        encoding='utf-8',
        buffer_size=1000,
        flush_interval=300
    )
    general_handler.setLevel(logging.INFO)
    general_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    general_handler.setFormatter(general_formatter)
    general_handler.addFilter(lambda record: logging.INFO <= record.levelno < logging.ERROR)
    logging.getLogger().addHandler(general_handler)

    error_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'error.log'),
        when='midnight',
        interval=1,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('\n[%(asctime)s]\nERROR: %(message)s\n' + '-'*50)
    error_handler.setFormatter(error_formatter)
    error_handler.addFilter(lambda record: record.levelno == logging.ERROR)
    logging.getLogger().addHandler(error_handler)

    critical_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'critical.log'),
        when='midnight',
        interval=1,
        encoding='utf-8'
    )
    critical_handler.setLevel(logging.CRITICAL)
    critical_formatter = logging.Formatter('\n[%(asctime)s]\nCRITICAL: %(message)s\n' + '-'*50)
    critical_handler.setFormatter(critical_formatter)
    logging.getLogger().addHandler(critical_handler)

    console_handler = colorlog.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s[%(asctime)s] %(levelname)s: %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'black,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)

    logging.getLogger().setLevel(log_level)
    atexit.register(cleanup_logger)

    # Start periodic flush tasks for buffered handlers
    loop = asyncio.get_event_loop()
    for handler in logging.getLogger().handlers:
        if isinstance(handler, AsyncBufferedTimedRotatingFileHandler):
            handler._flush_task = loop.create_task(handler.periodic_flush())
