
import click
import json
import subprocess
import re
import sys

from ruamel.yaml import YAML

def get_versions_in_current_environment(envname='base'):
    assert re.match(r'[a-zA-Z0-9]+$', envname), (
        'illegal environment name "{}"'.format(envname))

    conn = subprocess.Popen(
        ['conda', 'env', 'export', '-n', envname, '--json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    o, e = conn.communicate()
    if e:
        raise IOError(e.decode())

    return json.loads(o.decode())


def parse_conda_dependencies(conda_dependencies):
    formatted_dependencies = {'conda': {}}
    for dep in conda_dependencies:
        if isinstance(dep, dict):
            for k, v in dep.items():
                if k not in formatted_dependencies:
                    formatted_dependencies[k] = {}
                for subdep in v:
                    formatted_dependencies[k].update({subdep.split('=')[0]: subdep})
        else:
            formatted_dependencies['conda'].update({dep.split('=')[0]: dep})

    return formatted_dependencies


def get_pinned_version(dependency, pinned_versions):
    if ('git+' in dependency) or ('http' in dependency):
        return dependency
    return pinned_versions.get(dependency.split('=')[0], dependency)


def pin_dependencies_in_conda_env_file_from_version_spec(
        filepath, versions_to_pin, dry_run=False):
    '''
    Parameters
    ----------
    '''

    indent_config = dict(mapping=2, sequence=2, offset=2)
    
    yaml = YAML(typ='rt')
    yaml.indent(**indent_config)
    yaml.default_flow_style = False

    with open(filepath, 'r') as f:
        file_spec = yaml.load(f)

    for di, dep in enumerate(file_spec['dependencies']):
        if isinstance(dep, dict):
            for k, v in dep.items():
                for si, subdep in enumerate(v):
                    pinned = get_pinned_version(subdep, versions_to_pin[k])
                    file_spec['dependencies'][di][k][si] = pinned
        else:
            pinned = get_pinned_version(dep, versions_to_pin['conda'])
            file_spec['dependencies'][di] = pinned

    if dry_run:
        sys.stdout.write("filename: {}\n{}\n".format(filepath, '-'*50))
        with YAML(output=sys.stdout) as yaml:
            yaml.indent(**indent_config)
            yaml.dump(file_spec)
        sys.stdout.write("\n")
    else:
        with open(filepath, 'w+') as f:
            yaml.dump(file_spec, f)


def pin_files(environment_files, dry_run=False):
    environment_specs = {}
    for envfile, envname in environment_files:
        if envname not in environment_specs:
            environment_specs[envname] = []
        environment_specs[envname].append(envfile)

    for envname in environment_specs:
        current_versions = get_versions_in_current_environment(envname)
        formatted_dependencies = parse_conda_dependencies(
            current_versions.get('dependencies', []))
        
        for envfile in environment_specs[envname]:
            pin_dependencies_in_conda_env_file_from_version_spec(
                envfile, formatted_dependencies, dry_run=dry_run)


@click.group()
def pinversions():
    pass


@pinversions.group()
def pin():
    pass


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def base(dry_run=False):
    pin_files([('base_environment.yml', 'base')], dry_run=dry_run)


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def notebook(dry_run=False):
    pin_files([('notebook/notebook_environment.yml', 'base')], dry_run=dry_run)


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def octave(dry_run=False):
    pin_files([('octave-worker/octave_environment.yml', 'base')], dry_run=dry_run)


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def r(dry_run=False):
    pin_files([('notebook/r_environment.yml', 'r')], dry_run=dry_run)


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def all(dry_run=False):
    pin_files(
        [
            ('base_environment.yml', 'base'),
            ('notebook/notebook_environment.yml', 'base'),
            ('octave-worker/octave_environment.yml', 'base'),
            ('notebook/r_environment.yml', 'r')],
        dry_run=dry_run)


if __name__ == "__main__":
    pin()
