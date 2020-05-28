import json

import falcon

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict


class AppError(Exception):
    meta = {"status": falcon.HTTP_500, "code": 500, "message": "Unknown Error"}

    def __init__(self, error=None):
        if error is None:
            error = AppError.meta
        self.error = error

    @property
    def code(self):
        return self.error["code"]

    @property
    def message(self):
        return self.error["message"]

    @property
    def status(self):
        return self.error["status"]

    @property
    def data(self):
        return self.error["data"]

    @staticmethod
    def handle(exception, req, res, error=None):
        res.status = exception.status
        meta = OrderedDict()
        meta["code"] = exception.code
        meta["message"] = exception.message
        if exception.data:
            res.body = json.dumps({"meta": meta, "data": exception.data})
        else:
            res.body = json.dumps({"meta": meta})


class NotSupportedError(AppError):
    meta = {"status": falcon.HTTP_405, "code": 405, "message": "Not Supported"}

    def __init__(self, method=None, url=None):
        super().__init__(NotSupportedError.meta)
        if method and url:
            self.error["data"] = "method: %s, url: %s" % (method, url)


class Unknown(AppError):
    meta = {
        "status": falcon.HTTP_500,
        "code": 500,
        "message": "Unknown Error",
    }

    def __init__(self, data=None):
        super().__init__(Unknown.meta)
        self.error["data"] = data


class BadRequest(AppError):
    meta = {
        "status": falcon.HTTP_400,
        "code": 400,
        "message": "Bad Request",
    }

    def __init__(self, data=None):
        super().__init__(BadRequest.meta)
        self.error["data"] = data


class Unauthorized(AppError):
    meta = {
        "status": falcon.HTTP_401,
        "code": 401,
        "message": "Unauthorized",
    }

    def __init__(self, data=None):
        super().__init__(Unauthorized.meta)
        self.error["data"] = data


class Forbidden(AppError):
    meta = {
        "status": falcon.HTTP_403,
        "code": 403,
        "message": "Forbidden",
    }

    def __init__(self, data=None):
        super().__init__(Forbidden.meta)
        self.error["data"] = data


class Conflict(AppError):
    meta = {
        "status": falcon.HTTP_409,
        "code": 409,
        "message": "Conflict / Requires Change",
    }

    def __init__(self, data=None):
        super().__init__(Conflict.meta)
        self.error["data"] = data
