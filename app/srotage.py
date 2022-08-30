import logging
from app.context import AppContext
import typing as tp
from app import models
import pickle


def get_waypoints(ctx: AppContext):
    if ctx.db.get("id"):
        result = pickle.loads(ctx.db.get("id"))
        logging.info("Waypoints was got from database")
        return result
    else:
        logging.info("There is no tasks in db")
        return None


def task_push(ctx: AppContext, waypoints: bytes):
    ctx.db.set("id", waypoints)
    logging.info("Databse record added")
