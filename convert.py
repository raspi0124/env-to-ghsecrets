import requests
import json
from base64 import b64encode
from nacl import encoding, public
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("env_file", help="Env File Path")
parser.add_argument("owner", help="Github Repository Owner")
parser.add_argument("repo", help="Github Repository Name")
parser.add_argument("token", help="Github Personal Access Token")


def get_publickey(GITHUB_TOKEN: str, GITHUB_USER: str, REPO_NAME: str) -> (str, str):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(
        f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/actions/secrets/public-key",
        headers=headers,
    )
    response_data = response.json()

    PUBLIC_KEY = response_data.get("key")
    PUBLIC_KEY_ID = response_data.get("key_id")

    return PUBLIC_KEY, PUBLIC_KEY_ID


def encrypt(public_key: str, secret_value: str) -> str:
    # https://www.nullpo.io/2020/05/21/git-github-api-secret/
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def post(
    GITHUB_TOKEN: str,
    GITHUB_USER: str,
    REPO_NAME: str,
    SECRET_NAME: str,
    SECRET_VALUE: str,
) -> bool:
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    PUBLIC_KEY, PUBLIC_KEY_ID = get_publickey(GITHUB_TOKEN, GITHUB_USER, REPO_NAME)

    ENCRYPTED_VALUE = encrypt(PUBLIC_KEY, SECRET_VALUE)

    payload = json.dumps({"encrypted_value": ENCRYPTED_VALUE, "key_id": PUBLIC_KEY_ID})

    response = requests.put(
        f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/actions/secrets/{SECRET_NAME}",
        headers=headers,
        data=payload,
    )

    if response.status_code == 204:
        print(f"Secret {SECRET_NAME} updated successfully.")
        return True
    else:
        print(
            f"Failed to update secret {SECRET_NAME}. Response code: {response.status_code}, Response message: {response.text}"
        )
        return False


def parse_env_file(env_file_path: str) -> dict:
    env_dict = {}
    with open(env_file_path, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.strip().split("=", 1)
            env_dict[key] = value
    return env_dict


def main():
    args = parser.parse_args()
    ENV_FILE_PATH = args.env
    GITHUB_TOKEN = args.token
    GITHUB_USER = args.user
    REPO_NAME = args.repo
    env_dict = parse_env_file(ENV_FILE_PATH)
    for key, value in env_dict.items():
        SECRET_NAME = key
        SECRET_VALUE = value
        post(GITHUB_TOKEN, GITHUB_USER, REPO_NAME, SECRET_NAME, SECRET_VALUE)


main()
