import json

import falcon
from cerberus import Validator

from app.errors import BadRequest

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

from app import log
from app.errors import NotSupportedError

LOG = log.get_logger()


def req_validator(req, res, resource, params, schema):
    LOG.debug(schema)
    v = Validator(schema)
    if not v.validate(req.media):
        raise BadRequest(v.errors)


class BaseController(object):
    health = {
        "server": "Codetaut auth API",
        "health": "OK"
    }

    def __to_json(self, body_dict):
        return json.dumps(body_dict)

    def on_error(self, res, error=None):
        res.status = error["status"]
        meta = OrderedDict()
        meta["code"] = error["code"]
        meta["message"] = error["message"]

        obj = OrderedDict()
        obj["meta"] = meta
        res.body = self.__to_json(obj)

    def on_success(self, res, data=None):
        res.status = falcon.HTTP_200
        meta = OrderedDict()
        meta["code"] = 200
        meta["message"] = "OK"

        obj = OrderedDict()
        obj["meta"] = meta
        obj["data"] = data
        res.body = self.__to_json(obj)

    def on_get(self, req, res):
        if req.path == "/":
            res.status = falcon.HTTP_200
            res.body = self.__to_json(self.health)
        else:
            raise NotSupportedError(method="GET", url=req.path)

    def on_post(self, req, res):
        raise NotSupportedError(method="POST", url=req.path)

    def on_put(self, req, res):
        raise NotSupportedError(method="PUT", url=req.path)

    def on_delete(self, req, res):
        raise NotSupportedError(method="DELETE", url=req.path)
