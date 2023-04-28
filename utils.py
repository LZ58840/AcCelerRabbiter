import errno
import os
import sys
from contextlib import contextmanager
from pathlib import Path

import pymysql
from dotenv import load_dotenv


DOCKER = False


@contextmanager
def database_ctx(auth):
    con = pymysql.connect(**auth)
    cur = con.cursor(pymysql.cursors.DictCursor)
    try:
        yield cur
    finally:
        con.commit()
        cur.close()
        con.close()


def get_mysql_auth(docker=DOCKER):
    try:
        return {
            "host": "rc_mysql" if docker else "localhost",
            "user": "animewallpaperbot",
            "password": os.environ['MYSQL_PASS'],
            "db": "awb",
        }

    except KeyError as e:
        _raise_env_missing(e)


def get_mysql_root_auth(docker=DOCKER):
    try:
        return {
            "host": "rc_mysql" if docker else "localhost",
            "user": "root",
            "password": os.environ['MYSQL_ROOT_PASS'],
            "db": "awb",
        }

    except KeyError as e:
        _raise_env_missing(e)


def get_rabbitmq_auth(docker=DOCKER):
    try:
        return {
            "host": "rc_rabbitmq" if docker else "localhost",
            "login": "animewallpaperbot",
            "password": os.environ['RABBITMQ_PASS'],
        }

    except KeyError as e:
        _raise_env_missing(e)


def _raise_env_missing(e: KeyError):
    print(f"Value {e.args[0]} is not set. "
          "Please ensure all values are set in the file `.env`. "
          "You may need to complete and rename the example file `.env-example`.",
          file=sys.stderr)
    sys.exit(errno.ENOENT)


dotenv_path = Path(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".env"))
if not load_dotenv(dotenv_path=dotenv_path):
    print("Couldn't load the configuration file. "
          "Please ensure the file `.env` is in the same directory as the executable. "
          "You may need to complete and rename the example file `.env-example`.",
          file=sys.stderr)
    sys.exit(errno.ENOENT)
