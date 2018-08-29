# -*- coding: utf-8 -*-
"""
    app.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from redis import StrictRedis
from flask_mail import Mail
from flask_oauthlib.client import OAuth
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_login import LoginManager

from apps.core.flask.myflask import App
from apps.core.flask.cache import Cache
from apps.core.db.mongodb import PyMongo
from apps.core.logger.logging import Logger, start_logger
from apps.configs.db_config import DB_CONFIG


start_logger.info("Initialize the application")
app = App(__name__)

db_site = PyMongo()
db_sys = PyMongo()
db_user = PyMongo()

cache = Cache()

start_logger.info("Initialize third-party libraries")
csrf = CSRFProtect()
login_manager = LoginManager()
session = Session()

mail = Mail()
logger = Logger()
oauth = OAuth()
redis = StrictRedis(host=DB_CONFIG["redis"]["host"],
                    port=DB_CONFIG["redis"]["port"],
                    password=DB_CONFIG["redis"]["password"])







