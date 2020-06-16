'''
Functions and command line app for manipulating conda environment specs

Usage
-----

.. code-block:: bash

    $ python pin.py pin all
    
    $ python pin.py unpin all

Use the ``--dry-run`` flag to see the effect of any commands rather than modifying the
environment files directly. The ``--help`` command provides additional information about
each command.
    
'''

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


def _determine_pinned_version(dependency, pinned_versions):
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
    comment : str or None
        Comment to include in file if a pinning flag should be included
    '''
    if ('git+' in dependency) or ('http' in dependency):
        return dependency, None

    if '=' in dependency:
        comment = 'pinkeep: {}'.format(dependency)
    else:
        comment = None

    return pinned_versions.get(dependency.split('=')[0], dependency), comment


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
                    pinned, comment = _determine_pinned_version(
                        subdep, versions_to_pin[k])

                    file_spec['dependencies'][di][k][si] = pinned
                    if comment is not None:
                        file_spec['dependencies'][di][k].yaml_add_eol_comment(
                            comment, si)
        else:
            pinned, comment = _determine_pinned_version(dep, versions_to_pin['conda'])
            file_spec['dependencies'][di] = pinned
            
            if comment is not None:
                file_spec['dependencies'].yaml_add_eol_comment(
                    comment, di)

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


def _unpin_dependency(tree, key):
    '''
    Determines the unpinned spec for individual packages based on comments and spec
    '''

    ct = tree.ca.items.get(key)
    if ct:
        comment = ct[0].value.strip()
        if 'pinkeep:' in comment:
            pinned = comment.split('pinkeep:')[1].strip()
            del tree.ca.items[key]
            return pinned

    pkg = tree[key]

    if ('http:' in pkg) or ('https:' in pkg) or ('git+' in pkg) or ('ssh+' in pkg):
        return pkg

    return pkg.split('=')[0]


def unpin_dependencies_in_conda_env_file(filepath, dry_run=False):
    '''
    Un-pin dependencies in conda environment file
    
    If encounters dependencies with ``# pinkeep: pkg=vers`` directives, these are
    preserved verbatim in the final spec.
    
    Paramters
    ---------
    filepath : str
        Path to the environment file to unpin
    dry_run : bool, optional
        Print rather than modify the environment file
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
                    file_spec['dependencies'][di][k][si] = _unpin_dependency(
                        file_spec['dependencies'][di][k], si)

        else:
            file_spec['dependencies'][di] = _unpin_dependency(
                file_spec['dependencies'], di)

    if dry_run:
        sys.stdout.write("filename: {}\n{}\n".format(filepath, '-'*50))
        with YAML(output=sys.stdout) as yaml:
            yaml.indent(**indent_config)
            yaml.dump(file_spec)
        sys.stdout.write("\n")
    else:
        with open(filepath, 'w+') as f:
            yaml.dump(file_spec, f)


def unpin_files(environment_files, dry_run=False):
    '''
    Unpin package versions in provided environment files
    
    Parameters
    ----------
    environment_files : list of tuples
        List of (environment file path, pin source env name) tuples to be pinned. The
        second tuple element will be used as the source environment on the local
        machine to look for pinned versions.
    dry_run : bool
        Print the updated environment files, rather than overwriting them. Default
        False.
    '''
    for envfile, envname in environment_files:
        unpin_dependencies_in_conda_env_file(envfile, dry_run=dry_run)


@click.group()
def pinversions():
    '''View and modify package version pins'''
    pass


@pinversions.command()
@click.argument(
    'file', default='all')
@click.option(
    '--dry-run',
    is_flag=True,
    default=False,
    help='print proposed spec rather than modifying it',
)
def pin(file, dry_run):
    '''Pin packages in environment files based on environments on the local machine'''
    
    spec_files = [
            ('base_environment.yml', 'base'),
            ('notebook/notebook_environment.yml', 'base'),
            ('octave-worker/octave_environment.yml', 'base'),
            ('notebook/r_environment.yml', 'r')]
    
    if file == 'all':
        pin_files(spec_files, dry_run=dry_run)
    elif file == 'base':
        pin_files([spec_files[0]], dry_run=dry_run)
    elif file == 'notebook':
        pin_files([spec_files[1]], dry_run=dry_run)
    elif file == 'octave':
        pin_files([spec_files[2]], dry_run=dry_run)
    elif file == 'r':
        pin_files([spec_files[3]], dry_run=dry_run)
    else:
        raise ValueError(
            'env type not recognized: {}'
            'choose from "base", "notebook", "octave", "r", or "all".'
            .format(file))

        
@pinversions.command()
@click.argument(
    'file', default='all')
@click.option(
    '--dry-run',
    is_flag=True,
    default=False,
    help='print proposed spec rather than modifying it',
)
def unpin(file, dry_run):
    '''Unpin packages in environment files'''
    
    spec_files = [
            ('base_environment.yml', 'base'),
            ('notebook/notebook_environment.yml', 'base'),
            ('octave-worker/octave_environment.yml', 'base'),
            ('notebook/r_environment.yml', 'r')]
    
    if file == 'all':
        unpin_files(spec_files, dry_run=dry_run)
    elif file == 'base':
        unpin_files([spec_files[0]], dry_run=dry_run)
    elif file == 'notebook':
        unpin_files([spec_files[1]], dry_run=dry_run)
    elif file == 'octave':
        unpin_files([spec_files[2]], dry_run=dry_run)
    elif file == 'r':
        unpin_files([spec_files[3]], dry_run=dry_run)
    else:
        raise ValueError(
            'env type not recognized: {}'
            'choose from "base", "notebook", "octave", "r", or "all".'
            .format(file))


if __name__ == "__main__":
    pinversions()
