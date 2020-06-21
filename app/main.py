import falcon

from app.base import BaseController
from app.errors import AppError
from app.password.controller import PasswordController
from app.session.controller import SessionController


class App(falcon.API):

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.add_route("/", BaseController())
        self.add_route("/session", SessionController())
        self.add_route("/password/", PasswordController())
        self.add_route("/password/create", PasswordController(), suffix="new_password")
        self.add_route("/password/reset", PasswordController(), suffix="reset")
        self.add_error_handler(AppError, AppError.handle)


wsgi_app = App()
