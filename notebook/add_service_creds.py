import json, yaml, os, glob


def add_service_creds():

    with open('/home/jovyan/worker-template.yml', 'r') as f:
        WORKER_TEMPLATE = yaml.safe_load(f)

    for env in WORKER_TEMPLATE['spec']['containers'][0]['env']:
        if 'GCSFUSE_TOKEN' in env['name']:
            print('token already appended')
            return

    creds = {}

    for f in glob.glob('/home/jovyan/service-account-credentials/*.json'):
        bucket = os.path.splitext(os.path.basename(f))[0]

        with open(f, 'r') as f:
            creds[bucket] = json.load(f)

    WORKER_TEMPLATE['spec']['containers'][0]['env'].append(
        {'name': 'GCSFUSE_TOKENS', 'value': json.dumps(creds)})

    with open('/home/jovyan/worker-template.yml', 'w') as f:
        f.write(yaml.dump(WORKER_TEMPLATE))

    print('worker-template.yml updated')


if __name__ == '__main__':
    add_service_creds()
