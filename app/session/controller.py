import falcon

from app import log
from app.base import BaseController, req_validator
from app.session.service import create

LOG = log.get_logger()


class SessionController(BaseController):

    @falcon.before(req_validator, {
        "username": {"type": "string", "required": True},
        "password": {"type": "string", "required": True}
    })
    def on_post(self, req, res):
        req_data = req.media
        res_data = create(req_data["username"], req_data["password"])
        self.on_success(res, res_data)
