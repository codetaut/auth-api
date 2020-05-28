import falcon

from app.base import BaseController, req_validator
from app.password.service import create_new_password, request_reset_password, update_password_with_otp, update_password


class PasswordController(BaseController):

    @falcon.before(req_validator, {
        "username": {"type": "string", "required": True},
        "temporaryPassword": {"type": "string", "required": True},
        "newPassword": {"type": "string", "required": True}
    })
    def on_post_new_password(self, req, res):
        req_data = req.media
        create_new_password(req_data["username"], req_data["temporaryPassword"], req_data["newPassword"])
        self.on_success(res)

    @falcon.before(req_validator, {
        "username": {"type": "string", "required": True}
    })
    def on_post_reset(self, req, res):
        req_data = req.media
        request_reset_password(req_data["username"])
        self.on_success(res)

    @falcon.before(req_validator, {
        "username": {"type": "string", "required": True},
        "password": {"type": "string", "required": True},
        "otp": {"type": "string", "required": True}
    })
    def on_post(self, req, res):
        req_data = req.media
        update_password_with_otp(req_data["username"], req_data["password"], req_data["otp"])
        self.on_success(res)

    @falcon.before(req_validator, {
        "username": {"type": "string", "required": True},
        "oldPassword": {"type": "string", "required": True},
        "newPassword": {"type": "string", "required": True}
    })
    def on_put(self, req, res):
        req_data = req.media
        update_password(req_data["username"], req_data["oldPassword"], req_data["newPassword"])
        self.on_success(res)
