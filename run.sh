set -e

skipTest=false
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# If you only want to get temporary credentials
# without starting the stack
setup_security_credentials() {
  echo "Fetching credentials"

  unset AWS_ACCESS_KEY_ID
  unset AWS_SECRET_ACCESS_KEY
  unset AWS_SESSION_TOKEN
  unset PROFILE

  echo "Enter AWS profile configured from aws cli" && read -r PROFILE
  echo "Chosen profile : ${PROFILE}"

  arn=$(aws sts get-caller-identity --query "Arn" --profile "${PROFILE}")
  # shellcheck disable=SC2086
  MAIL=$(echo ${arn} | grep -E -o '\b[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+.[a-zA-Z0-9.-]+\b')
  echo "${MAIL}"

  MFA_SERIAL=$(echo "${arn}" | grep -E -o '[0-9]{12}')
  # shellcheck disable=SC2086
  echo ${MFA_SERIAL}
  ROLE_ARN=arn:aws:iam::965776723730:role/DefaultAccountAccessRole

  echo "Enter MFA code:" && read -r MFA_CODE
  echo "Entered MFA code: ${MFA_CODE}"

  get_session_token_res=$(
    aws sts assume-role \
    --role-arn ${ROLE_ARN} \
    --role-session-name "session-$(GuidGen)" \
    --duration 43200 \
    --profile "${PROFILE}" \
    --serial-number "arn:aws:iam::${MFA_SERIAL}:mfa/${MAIL}" \
    --token-code "${MFA_CODE}"
  )
  echo "${get_session_token_res}"

  export AWS_ACCESS_KEY_ID=$(echo "${get_session_token_res}" | python -c 'import json, sys;obj=json.load(sys.stdin);print(obj["Credentials"]["AccessKeyId"])')
  export AWS_SECRET_ACCESS_KEY=$(echo "${get_session_token_res}" | python -c 'import json, sys;obj=json.load(sys.stdin);print(obj["Credentials"]["SecretAccessKey"])')
  export AWS_SESSION_TOKEN=$(echo "${get_session_token_res}" | python -c 'import json, sys;obj=json.load(sys.stdin);print(obj["Credentials"]["SessionToken"])')

  echo "
  COPY AND EXECUTE THESE LINES IN TERMINAL WINDOW YOU START intelliJ OR USE DevAccountAccessRole:

  export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
  export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
  export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN

  "
}

start_consumerservices() {
  echo "Starting consumer services"

  if [[ "$skipTest" == false ]]; then
    ./gradlew consumerserver:test
  fi

  ./gradlew consumerserver:jibDockerBuild
  docker-compose -f infrastructure/docker-compose-development.yml build consumer-client
  docker-compose -f infrastructure/docker-compose-development.yml run --rm start_dependencies
  docker-compose -f infrastructure/docker-compose-development.yml up -d consumer-client
}

process_arg() {

  # check if second arg is to skip the tests
  if [[ "$2" == "skipTest" ]]; then
    skipTest=true
  fi

  setup_security_credentials

  if [[ "$1" == "consumer" ]]; then
    start_consumerservices
  elif [[ "$1" == "admin" ]]; then
    start_adminservices
  elif [[ "$1" == "all" ]]; then
    start_all
  else
    echo "Unknown parameter $1"
  fi
}

echo "Processing command $@"

pushd "${PROJECT_ROOT}"

# check if multiparams eg: mobile,admin
if [[ "$1" == *","* ]]; then
  # split the args and run each services
  IFS=',' read -ra services <<<"$1"
  for i in "${services[@]}"; do
    process_arg "${i}" "$2"
  done
elif [[ "$1" == "credentials" ]]; then
  setup_security_credentials
  exit 1
else
  # run a single service
  if [[ "$1" == "kill" ]]; then
    docker-compose -f infrastructure/docker-compose-development.yml down -v
  else
    process_arg "$1" "$2"
    # attach the container logs to the terminal
    docker-compose -f infrastructure/docker-compose-development.yml logs -f
  fi
fi

popd
