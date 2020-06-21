from invoke import task
from shutil import which
from configparser import ConfigParser
import os
from subprocess import run, PIPE, STDOUT
import re
import enum
import uuid
import json
from sys import exit
from server import serve, live


def command(exe=None, *args):
    """Construct a console command from a list of arguments."""
    executable = which(exe)
    if executable:
        result = run([executable, *args], stdout=PIPE, stderr=STDOUT)
        if result.stderr is not None:
            raise Exception(f"Command was unsuccessful: {[executable, *args]}")
        return result.stdout.decode('utf-8')
    else:
        raise FileNotFoundError(exe)


class Env(enum.Enum):
    sbx = "sbx"
    dev = "dev"
    tst = "tst"
    prd = "prd"


ep = "\nError:"
err = lambda stm: print(f"{ep} {stm}")
sts = lambda *args: command("aws", "sts", *args)
cf = lambda *args: command("aws", "cloudformation", *args)


@task
def credentials(ctx):
    print("Fetching credentials")
    profile = input("Enter AWS profile configured from aws cli: ")
    arn = sts("get-caller-identity", "--query", "Arn", "--profile", profile)
    if re.match(r"(The config profile \(.*\) could not be found)", arn.strip()):
        err(f"Profile ({profile}) not found in your AWS CLI configuration")
        exit(1)
    mail = re.findall(r"[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+.[a-zA-Z0-9.-]+", arn)[0]
    mfa_serial = re.findall(r"[0-9]{12}", arn)[0]
    role_arn = "arn:aws:iam::965776723730:role/DefaultAccountAccessRole"
    print(f"Signing into AWS account ({mfa_serial}) with email: {mail}")
    mfa_code = input("Enter MFA code: ")
    get_session_token_res = sts("assume-role", "--role-arn", role_arn, "--role-session-name",
                                f"session-{uuid.uuid1()}", "--duration", "43200", "--profile",
                                profile, "--serial-number", f"arn:aws:iam::{mfa_serial}:mfa/{mail}",
                                "--token-code", mfa_code)
    if get_session_token_res.strip().startswith("An error occurred"):
        err(f"{get_session_token_res.strip()}")
        exit(1)
    obj = json.loads(get_session_token_res)
    print(f"""
COPY AND EXECUTE THESE LINES IN TERMINAL WINDOW YOU START intelliJ OR USE DevAccountAccessRole:
        
export AWS_ACCESS_KEY_ID={obj["Credentials"]["AccessKeyId"]}
export AWS_SECRET_ACCESS_KEY={obj["Credentials"]["SecretAccessKey"]}
export AWS_SESSION_TOKEN={obj["Credentials"]["SessionToken"]}""")
    with open(".aws.env", "w") as f:
        f.write('[default]\n')
        f.write(f'AWS_ACCESS_KEY_ID={obj["Credentials"]["AccessKeyId"]}\n')
        f.write(f'AWS_SECRET_ACCESS_KEY={obj["Credentials"]["SecretAccessKey"]}\n')
        f.write(f'AWS_SESSION_TOKEN={obj["Credentials"]["SessionToken"]}\n')


@task
def server(ctx, is_live=False):
    if is_live:
        live()
    else:
        serve()


@task
def deploy(ctx):
    command("docker-compose", "-f", "docker-compose.yml", "up", "-d", "--build")


@task
def read_credentials(ctx):
    config = ConfigParser()
    config.read(".aws.env")
    os.environ["AWS_ACCESS_KEY_ID"] = config["default"]["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = config["default"]["AWS_SECRET_ACCESS_KEY"]
    os.environ["AWS_SESSION_TOKEN"] = config["default"]["AWS_SESSION_TOKEN"]


@task(read_credentials)
def stack(ctx):
    env_key = input(f"Choose environment to deploy {[val.value for val in Env]}: ")
    try:
        env = Env[env_key]
    except Exception as e:
        print(repr(e))
        exit(1)
    print(os.environ["AWS_ACCESS_KEY_ID"])
    # cf("deploy", "--stack-name")
