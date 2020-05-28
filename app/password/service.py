from app import log
from app.config import CONFIG
from app.errors import BadRequest, Conflict
from app.session.service import create
from app.utility.aws import idp

LOG = log.get_logger()

cognito_clientId = CONFIG["aws"]["cognito_clientId"]
cognito_userPoolId = CONFIG["aws"]["cognito_userPoolId"]


def create_new_password(username, temporary_password, new_password):
    try:
        create(username, temporary_password)
    except Conflict as ex:
        challenge = ex.data.get("challenge")
        session = ex.data.get("session")
        if challenge and challenge == "NEW_PASSWORD_REQUIRED":
            try:
                idp().admin_respond_to_auth_challenge(
                    ChallengeName="NEW_PASSWORD_REQUIRED",
                    UserPoolId=cognito_userPoolId,
                    ClientId=cognito_clientId,
                    ChallengeResponses={
                        "USERNAME": username,
                        "PASSWORD": temporary_password,
                        "NEW_PASSWORD": new_password
                    },
                    Session=session
                )
            except Exception as ex:
                LOG.debug(repr(ex))
                raise BadRequest(str(ex))


def request_reset_password(username):
    try:
        idp().admin_reset_user_password(
            UserPoolId=cognito_userPoolId,
            Username=username
        )
    except Exception as ex:
        LOG.debug(repr(ex))
        raise BadRequest(str(ex))


def update_password_with_otp(username, password, otp):
    try:
        idp().confirm_forgot_password(
            ClientId=cognito_clientId,
            Username=username,
            ConfirmationCode=otp,
            Password=password
        )
    except Exception as ex:
        LOG.debug(repr(ex))
        raise BadRequest(str(ex))


def update_password(username, old_password, new_password):
    try:
        create_session_response = create(username, old_password)
        idp().change_password(
            PreviousPassword=old_password,
            ProposedPassword=new_password,
            AccessToken=create_session_response
        )
    except Exception as ex:
        LOG.debug(repr(ex))
        raise BadRequest(str(ex))
