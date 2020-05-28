from app import log
from app.config import CONFIG
from app.errors import Unauthorized, Conflict
from app.utility.aws import idp

LOG = log.get_logger()

cognito_clientId = CONFIG["aws"]["cognito_clientId"]
cognito_userPoolId = CONFIG["aws"]["cognito_userPoolId"]


def create(username, password):
    response = {}
    try:
        aws_response = idp().initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password
            },
            ClientId=cognito_clientId
        )
    except Exception as ex:
        LOG.debug(repr(ex))
        raise Unauthorized(str(ex))
    challenge = aws_response.get("ChallengeName")
    if challenge:
        response["challenge"] = challenge
        response["session"] = aws_response["Session"]
        raise Conflict(response)
    else:
        response = aws_response["AuthenticationResult"]["AccessToken"]
    return response
