import json, yaml


def add_service_creds():

    with open('/home/jovyan/worker-template.yml', 'r') as f:
        WORKER_TEMPLATE = yaml.safe_load(f)

    for env in WORKER_TEMPLATE['spec']['containers'][0]['env']:
        if 'GCSFUSE_TOKEN' in env['name']:
            print('token already appended')
            return

    with open('/home/jovyan/service-account-credentials.json', 'r') as f:
        print('loading service account creds')
        TOKEN_STRING = json.dumps(json.load(f))

    WORKER_TEMPLATE['spec']['containers'][0]['env'].append(
        {'name': 'GCSFUSE_TOKEN', 'value': TOKEN_STRING})

    with open('/home/jovyan/worker-template.yml', 'w') as f:
        f.write(yaml.dump(WORKER_TEMPLATE))

    print('worker-template.yml updated')


if __name__ == '__main__':
    add_service_creds()
