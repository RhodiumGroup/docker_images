'''
Run an SQL proxy server to enable connections to a cloud sql instance

To use, create a file at /home/jovyan/setup.cfg with the following contents:

.. code-block:: bash

    [sql-proxy]

    SQL_INSTANCE = {project}:{region}:{instance}=tcp:{port}
    SQL_TOKEN_FILE = /path/to/credentials-file.json

modifying the `SQL_INSTANCE` and `SQL_TOKEN_FILE` values to match your server's
configuration.

Then, run `python run_sql_proxy.py`. This will start an SQL proxy and will also
add these credentials to your ~/worker-template.yml file.

When the process is killed (through `^C` or by killing the process) the worker
template will be returned to its previous state.

'''

import os
import json
import yaml
import configparser
import subprocess
import signal
import time


def get_sql_service_account_token(sql_token_file):
    if sql_token_file is None:
        return

    try:
        with open(sql_token_file, 'r') as f:
            return json.load(f)

    except (OSError, IOError):
        return


class add_sql_proxy_to_worker_spec(object):
    kill_now = False

    def __init__(self, sql_instance, sql_token):
        self.original_worker_template = None
        self.sql_instance = sql_instance
        self.sql_token = sql_token

        self.sql_proxy_process = None
        
        # handle sigint
        signal.signal(signal.SIGINT, self.return_worker_spec_to_original_state)
        signal.signal(signal.SIGTERM, self.return_worker_spec_to_original_state)

    def __enter__(self):
        sql_instance = self.sql_instance
        sql_token = self.sql_token

        if (sql_instance is None) or (sql_token is None):
            return

        try:
            with open('/home/jovyan/worker-template.yml', 'r') as f:
                self.original_worker_template = f.read()
                worker_template_modified = yaml.safe_load(self.original_worker_template)
        
        except (OSError, IOError, ValueError):
            return
            
        env_vars = []

        for env in worker_template_modified['spec']['containers'][0]['env']:
            if 'SQL_INSTANCE' in env['name']:
                continue
            elif 'SQL_TOKEN_FILE' in env['name']:
                continue
            else:
                env_vars.append(env)

        env_vars.append(
            {'name': 'SQL_TOKEN', 'value': json.dumps(sql_token)})

        env_vars.append(
            {'name': 'SQL_INSTANCE', 'value': sql_instance})
        
        worker_template_modified['spec']['containers'][0]['env'] = env_vars

        with open('/home/jovyan/worker-template.yml', 'w') as f:
            f.write(yaml.dump(worker_template_modified))

        print('proxy added to worker-template.yml')


    def maybe_start_sql_proxy(self, sql_instance, sql_token_file):
        if (sql_instance is None) or (sql_token_file is None):
            return
        
        p = subprocess.Popen([
            '/usr/bin/cloud_sql_proxy',
            '-instances',
            sql_instance,
            '-credential_file',
            sql_token_file])

        self.sql_proxy_process = p

        p.wait()


    def return_worker_spec_to_original_state(self, *args):
        if self.original_worker_template is None:
            return

        with open('/home/jovyan/worker-template.yml', 'w') as f:
            f.write(self.original_worker_template)        

        print('proxy removed from worker-template.yml')

        if (
                (self.sql_proxy_process is not None)
                and (self.sql_proxy_process.poll() is None)):

            try:
                self.sql_proxy_process.kill()
            except:
                pass
        
        self.kill_now = True


    def __exit__(self, *errs):
        self.return_worker_spec_to_original_state()


def handle_sql_config():
    config = configparser.ConfigParser()

    if not os.path.isfile('/home/jovyan/setup.cfg'):
        return

    config.read('/home/jovyan/setup.cfg')
    
    if not 'sql-proxy' in config.sections():
        return

    sql_instance = config['sql-proxy'].get('SQL_INSTANCE')
    sql_token_file = config['sql-proxy'].get('SQL_TOKEN_FILE')
    sql_token = get_sql_service_account_token(sql_token_file)

    sql_proxy = add_sql_proxy_to_worker_spec(sql_instance, sql_token)
    
    with sql_proxy:
        sql_proxy.maybe_start_sql_proxy(sql_instance, sql_token_file)

    # wait for sql_proxy to exit gracefully
    while True:
        if sql_proxy.kill_now:
            break

        time.sleep(1)


if __name__ == "__main__":
    handle_sql_config()
