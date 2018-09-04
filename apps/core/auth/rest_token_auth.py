# -*- coding: utf-8 -*-
"""
    rest_token_auth.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from random import randint
from uuid import uuid1
from bson import ObjectId
from flask import current_app, request
from werkzeug.exceptions import Unauthorized
from apps.app import db_sys, cache, rest_session
from apps.configs.sys_config import REST_SECRET_TOKEN_CACHE_KEY, REST_SECRET_TOKEN_CACHE_TIMEOUT
from apps.core.utils.get_config import get_config
from apps.utils.format.obj_format import obj_id_to_str
import base64
import time


class SecretTokenError(Unauthorized):
    description = "SecretToken in RestToken is invalid"


class AccessTokenError(Unauthorized):
    description = "AccessToken in RestToken is invalid"


class TokenError(Unauthorized):
    description = "Rest Token validation failed"


class RestTokenAuth(object):
    @staticmethod
    def encode_auth_token():
        id_ = "{}{}".format(str(uuid1()), randint(0, 999999))
        return {
            "token": base64.b16decode(id_.encode()).decode()
        }

    def create_secret_token(self):
        tokens = db_sys.db.sys_token.find({"token_type": "secret_token"})
        if tokens.count(True) < 2:
            result = self.encode_auth_token()
            token = {
                "token_type": "secret_token",
                "key": result["token"],
                "token": result["token"],
                "is_active": 1,
                "time": time.time()
            }
            r = db_sys.db.sys_token.insert_one(token)
            token["_id"] = str(r.inserted_id)
            cache.delete(REST_SECRET_TOKEN_CACHE_KEY)
            return True, token
        return False, "Create up to 2 tokens"

    def activate_secret_token(self, token_id):
        r = db_sys.db.sys_token.update_one(
            {"_id": ObjectId(token_id)},
            {"$set": {"is_active": 1}}
        )
        if r.modified_count:
            cache.delete(REST_SECRET_TOKEN_CACHE_KEY)
            return True, "Activate token successfully"
        else:
            return False, "Activate token failed"

    def disable_secret_token(self, token_id):
        if db_sys.db.sys_token.find({
            "token_type": "secret_token",
            "is_active": {"$in": [1, True]}
        }).count(True) > 1:
            r = db_sys.db.sys_token.update_one({"_id": ObjectId(token_id)},
                                               {"$set": {"is_active": 0}})
            if r.modified_count:
                cache.delete(REST_SECRET_TOKEN_CACHE_KEY)
                return True, "Disable token successfully"
            else:
                return False, "Disable token failed"
        else:
            return False, "Keep at least one active token"

    def delete_secret_token(self, token_id):
        if db_sys.db.sys_token.find({"token_type": "secret_token"}).count(True) > 1:
            r = db_sys.db.sys_token.delete_one({"_id": ObjectId(token_id)})
            if r.deleted_count > 0:
                return True, "Successfully deleted"
            else:
                return False, "Delete failed"
        else:
            return False, "Delete failed, keep at least one token"

    @property
    @cache.cached(key=REST_SECRET_TOKEN_CACHE_KEY, timeout=REST_SECRET_TOKEN_CACHE_TIMEOUT)
    def get_secret_tokens(self):
        token_info = db_sys.db.sys_token.find({"token_type": "secret_token"})
        if not token_info.count(True):
            s, r = self.create_secret_token()
            token_info = [r]
        else:
            token_info = obj_id_to_str(token_info)

        is_active_token = []
        for token in token_info:
            if token["is_active"]:
                is_active_token.append(token["token"])
        data = {
            "token_info": token_info,
            "is_active_token": is_active_token
        }
        return data

    def auth_rest_token(self):
        auth_token_type = None
        auth_header = request.headers.get("RestToken")
        if auth_header:
            is_malformed = False
            auth_header = auth_header.split(" ")
            if len(auth_header) >= 2:
                if auth_header[0] == "SecretToken":
                    auth_token_type = "secret_token"
                    if not auth_header[1] in self.get_secret_tokens["is_active_token"]:
                        response = current_app.make_response("Invalid SecretToken for RestToken")
                        raise SecretTokenError(response.get_data(as_text=True), response=response)
                elif auth_header[0] == "AccessToken":
                    auth_token_type = "access_token"
                    self.auth_access_token(auth_header[1])
                else:
                    is_malformed = True
            else:
                is_malformed = True

            if is_malformed:
                response = current_app.make_response("""
                    Token malformed, should be 'SecretToken<token>' 'AccessToken<token>' and 'ClientId <client_id>'
                    """)
                raise SecretTokenError(response.get_data(as_text=True), response=response)
        else:
            response = current_app.make_response("""
                Token is miss, unconventional web browsing requests please provide "RestToken", 
                otherwise provide "X-CSRFToken"
            """)
            raise TokenError(response.get_data(as_text=True), response=response)
        return auth_token_type

    def create_access_token(self):
        r = self.auth_rest_token()
        if r == "secret_token":
            client_token = {
                "token": self.encode_auth_token()["token"],
                "expiration": time.time() + get_config("rest_auth_token", "REST_ACCESS_TOKEN_LIFETIME")
            }
            sid = rest_session.set("session_token", client_token)
            if sid:
                data = {
                    "client_id": sid,
                    "access_token": client_token["token"]
                }
            else:
                data = {
                    "msg": "Failed to get, please try again",
                    "msg_type": "w",
                    "http_status": 400
                }
        else:
            data = {
                "msg": "The RestToken provided by the request header is not a SecretToken",
                "msg_type": "w",
                "http_status": 400
            }
        return data

    def auth_access_token(self, token):
        session_token = rest_session.get("access_token")
        if session_token:
            if session_token["token"] != token or session_token["expiration"] <= time.time():
                response = current_app.make_response("Invalid AccessToken or AccessToken has expired")
                raise AccessTokenError(response.get_data(as_text=True), response=response)
        else:
            response = current_app.make_response("Can not find the ClientId matching 'AccessToken'")
            raise AccessTokenError(response.get_data(as_text=True), response=response)








