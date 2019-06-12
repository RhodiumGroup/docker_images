import json, os


def create_service_cred_files():

    with open("/opt/gcsfuse_token_strings.json", 'r') as f:
        creds = json.load(f)

    for k, v in creds.items():
        with open('/opt/gcsfuse_tokens/{}.json'.format(k), 'w+') as f:
            f.write(json.dumps(v))


if __name__ == '__main__':
    create_service_cred_files()
