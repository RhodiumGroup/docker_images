import json, yaml, os, glob


def add_service_creds():

    with open('/home/jovyan/worker-template.yml', 'r') as f:
        WORKER_TEMPLATE = yaml.safe_load(f)
        
    env_vars = []
    creds = {}

    for env in WORKER_TEMPLATE['spec']['containers'][0]['env']:
        if 'GCSFUSE_TOKEN' in env['name']:
            continue
        elif 'GCSFUSE_TOKENS' in env['name']:
            creds.update(env['value'])
        else:
            env_vars.append(env)

    for f in glob.glob('/home/jovyan/service-account-credentials/*.json'):
        bucket = os.path.splitext(os.path.basename(f))[0]

        with open(f, 'r') as f:
            creds[bucket] = json.load(f)

    env_vars.append(
        {'name': 'GCSFUSE_TOKENS', 'value': json.dumps(creds)})
    
    WORKER_TEMPLATE['spec']['containers'][0]['env'] = env_vars

    with open('/home/jovyan/worker-template.yml', 'w') as f:
        f.write(yaml.dump(WORKER_TEMPLATE))

    print('worker-template.yml updated')


if __name__ == '__main__':
    add_service_creds()