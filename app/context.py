import redis
import typing as tp
import logging
from app import config


class AppContext:
    def __init__(self, secrets):
        self.db: tp.Optional[redis.Redis] = redis.Redis()
        logging.info('Redis started successfully')
        self.secrets = secrets

    async def on_startup(self, app=None):
        logging.info('Server started')

    async def on_shutdown(self, app=None):
        if self.db:
            if config.CLEAR_DB:
                self.db.flushdb()
                logging.info('DB cleared')
            self.db.close()
            logging.info('DB Closed')
