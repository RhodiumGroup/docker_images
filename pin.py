
import click
import json
import subprocess
import re
import sys

from ruamel.yaml import YAML

def get_versions_in_current_environment(envname='base'):
    '''
    Calls ``conda env export -n {envname} --json`` and returns spec
    
    Parameters
    ----------
    envname : str
        Name of environment to query (default 'base')
    
    Returns
    -------
    spec : dict
        Environment spec
    '''
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
    '''
    Splits conda dependencies into `conda` and other provider dependencies (e.g. `pip`)
    '''
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


def determine_pinned_version(dependency, pinned_versions):
    '''
    Handle individual packages and pinned versions to get package spec
    
    Defines the line-by-line logic that decides how the line from the original yaml
    file and the dependencies from the local environment should be used to construct
    the pinned dependency in the new spec file.
    
    Parameters
    ----------
    dependency : str
        Package name or spec from current environment file
    pinned_versions : dict
        Dictionary of package names and pinned versions from local environment
    
    Returns
    -------
    pinned : str
        Pinned package spec
    '''
    if ('git+' in dependency) or ('http' in dependency):
        return dependency
    return pinned_versions.get(dependency.split('=')[0], dependency)


def pin_dependencies_in_conda_env_file_from_version_spec(
        filepath, versions_to_pin, dry_run=False):
    '''
    Pin package versions to a given spec

    Parameters
    ----------
    filepath : str
        Conda environment yml file to be pinned
    versions_to_pin : dict
        Dictionary of package specs, with keys package sources (e.g. ``conda``,
        ``pip``), and values dictionaries of package names and pinned versions.
    dry_run : bool
        Print the updated environment files, rather than overwriting them. Default
        False.
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
                    pinned = determine_pinned_version(subdep, versions_to_pin[k])
                    file_spec['dependencies'][di][k][si] = pinned
        else:
            pinned = determine_pinned_version(dep, versions_to_pin['conda'])
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
    '''
    Pin package versions in provided environment files
    
    Parameters
    ----------
    environment_files : list of tuples
        List of (environment file path, pin source env name) tuples to be pinned. The
        second tuple element will be used as the source environment on the local
        machine to look for pinned versions.
    versions_to_pin : dict
        Dictionary of package specs, with keys package sources (e.g. ``conda``,
        ``pip``), and values dictionaries of package names and pinned versions.
    dry_run : bool
        Print the updated environment files, rather than overwriting them. Default
        False.
    '''
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
    '''View and modify package version pins'''
    pass


@pinversions.group()
def pin():
    '''Pin packages in environment files based on environments on the local machine'''
    pass


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def base(dry_run=False):
    '''Pin the base environment file'''
    pin_files([('base_environment.yml', 'base')], dry_run=dry_run)


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def notebook(dry_run=False):
    '''Pin the notebook base environment file'''
    pin_files([('notebook/notebook_environment.yml', 'base')], dry_run=dry_run)


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def octave(dry_run=False):
    '''Pin the worker octave environment files'''
    pin_files([('octave-worker/octave_environment.yml', 'base')], dry_run=dry_run)


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def r(dry_run=False):
    '''Pin the notebook r environment files'''
    pin_files([('notebook/r_environment.yml', 'r')], dry_run=dry_run)


@pin.command()
@click.option(
    '--dry-run', is_flag=True, default=False, help='print proposed spec rather than modifying it')
def all(dry_run=False):
    '''Pin all environment files'''
    pin_files(
        [
            ('base_environment.yml', 'base'),
            ('notebook/notebook_environment.yml', 'base'),
            ('octave-worker/octave_environment.yml', 'base'),
            ('notebook/r_environment.yml', 'r')],
        dry_run=dry_run)


if __name__ == "__main__":
    pin()
