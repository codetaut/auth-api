import boto3

from app.config import CONFIG


class Singleton(type):
    """ Singleton always return same session """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AWSSession(metaclass=Singleton):
    def __init__(self):
        self.session = None
        self.get_aws_session()

    def get_aws_session(self):
        """ return AWS session """
        if not self.session:
            self.session = boto3.Session(aws_access_key_id=CONFIG["aws"][
                "ACCESS_KEY_ID"], aws_secret_access_key=CONFIG["aws"]["SECRET_ACCESS_KEY"],
                                         region_name=CONFIG["aws"]["region"])
        return self.session


class AWSMapper:
    def __init__(self):
        self.session = None
        aws_obj = AWSSession()
        self.session = aws_obj.session

    def client(self, service):
        """ return aws client for specific service """
        if self.session:
            return self.session.client(service)
        return boto3.client(service)

    def resource(self, service):
        """ return aws resource for specific service """
        if self.session:
            return self.session.resource(service)
        return boto3.resource(service)


def idp():
    aws = AWSMapper()
    return aws.client('cognito-idp')
