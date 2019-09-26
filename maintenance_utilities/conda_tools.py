'''
Utilities for parsing and managing conda environments & dependencies

This module is used by the package alignment tests and (eventually) could be
used in tools to automatically find solutions for unified upgrades of multiple
connected environments. Additionally, we could develop tools to automate
environment pinning and other maintenance tasks.

TODO:

* account for upstream base notebook environment (ugh)
* build environments with "subdirs" specifying architecture of target servers

'''

import os
import re
import yaml
from conda.core.solve import Solver

CONDA_ARGS = {
    '-n': '--name',
    '-f': '--file',
    '-p': '--prefix',
    '-c': '--channel',
    '-S': '--satisfied-skip-solve',
    '-m': '--mkdir',
    '-C': '--use-index-cache',
    '-k': '--insecure',
    '-d': '--dry-run',
    '-q': '--quiet',
    '-v': '--verbose',
    '-y': '--yes'}


def get_conda_solver(
        filepath=None,
        prefix=None,
        channels=None,
        subdirs=None,
        specs_to_add=None,
        existing_solver=None):
    '''
    Initialize or update a conda environment solver from a file or spec

    Parameters
    ----------
    filepath : str, optional
        Path to a yaml file to parse and solve. If not provided, ``prefix`` is
        required and any transactions must be defined in ``channels``,
        ``subdirs``, and ``specs_to_add``.
    prefix : str, optional
        Name or path of the environment to be created/modified. Ignored if
        ``filepath`` is provided; required if omitted.
    channels: list, optional
        Conda channels. Ignored if ``filepath`` is provided.
    subdirs: tuple, optional
        Architecture subdirs. Ignored if ``filepath`` is provided.
    specs_to_add: list, optional
        List of strings of package specs to add to the environment. Ignored if
        ``filepath`` is provided.
    existing_solver : conda.core.solve.Solver, optional
        Optionally, upgrade a provided spec with the new dependencies provided
        in an environment file. Default is to create a new environment.

    Returns
    -------
    solver: conda.core.solve.Solver

    Examples
    --------

    Initializing with an environment file:

    .. code-block:: python

        >>> get_conda_solver('notebook/environment.yml')
        <conda.core.solve.Solver at ...>

    Initializing with a spec

    .. code-block:: python

        >>> s = get_conda_solver(
        ...         prefix='vis',
        ...         channels=['pyviz', 'conda-forge'],
        ...         specs_to_add=['python=3.7', 'holoviews', 'bokeh>=1.2'])
        ...

    Testing for unsatisfiable environments:

    .. code-block:: python

        >>> s = get_conda_solver(
        ...         prefix='base',
        ...         specs_to_add=['xarray>=0.13.0', 'python<3.0'])
        ...
        >>> s.solve_final_state()  # doctest: +ELLIPSIS
        ...
        Traceback (most recent calls last):
        ...
        UnsatisfiableError: The following specifications were found
        to be incompatible with the existing python installation in your environment:

          - xarray[version='>=0.13.0'] -> python[version='>=3.5.3']

        If python is on the left-most side of the chain, that's the version you've asked for.
        When python appears to the right, that indicates that the thing on the left is somehow
        not available for the python version you've asked for.
        Your current python version is (python[version='<3.0']).

        The following specifications were found to be incompatible with each other:

          - python[version='<3.0']

    TODO
    ----

    * figure out how to solve for/align pip dependencies. currently these are
      ignored

    '''

    if filepath is not None:
        with open(filepath, 'r') as f:
            spec = yaml.safe_load(f)
    else:
        spec = {
            'prefix': prefix,
            'channels': channels if channels is not None else [],
            'subdirs': subdirs if subdirs is not None else [],
            'dependencies': specs_to_add if specs_to_add is not None else []}

    # exclude pip dependencies - these trip up the Solver
    conda_packages = [
        d for d in spec.get('dependencies', []) if not isinstance(d, dict)]

    if existing_solver is None:
        solver = Solver(
            spec.get('name', 'base'),
            channels=spec.get('channels', []),
            specs_to_add=conda_packages)
    else:
        solver = Solver(
            prefix=existing_solver.prefix,
            channels=spec.get('channels', existing_solver.channels),
            subdirs=spec.get('subdirs', existing_solver.subdirs),
            specs_to_add=(list(existing_solver.specs_to_add) + conda_packages),
            specs_to_remove=spec.get(
                'specs_to_remove', existing_solver.specs_to_remove))

    return solver

def parse_conda_create_command(env, args):
    '''
    Convert a conda create/install/update command into a package spec

    TODO
    ----

    * accommodate ``conda remove`` command

    '''

    if args[0].strip().lower() != 'conda':
        return ('invalid', args)

    chaffe = ['conda', 'install', 'update', 'create', '-y', '--yes']
    install_args = [a for a in args if a.lower() not in chaffe]
    if len(install_args) == 1 and install_args[0].split('=')[0] == 'conda':
        # conda upgrade conda - take no action with API validation
        # return {'upgrade': install_args[0].strip('"\''))}
        pass

    spec = {'dependencies': []}

    get_install_args = iter(install_args)

    while True:
        try:
            arg = next(get_install_args)
        except StopIteration:
            break

        if arg.startswith('-'):
            spec[CONDA_ARGS.get(arg, arg).lstrip('-')] = next(get_install_args)

        else:
            pkgver = arg.strip('"\'')
            spec['dependencies'].append(pkgver)

    spec['name'] = spec.get('name', env)
    spec['channel'] = spec.get('channel', 'defaults')

    return spec


def get_conda_specs(dockerfile, conda_specs=None):
    '''
    Scours a docker file for conda commands, and returns a spec for each env

    Parameters
    ----------
    dockerfile: str
        Path to a Dockerfile
    conda_specs: dict, None
        Existing conda specs from the Dockerfile build dependencies

    Returns
    -------
    spec : dict
        Dictionary of ``(env: solver)`` pairs, where the env is the name of
        conda environments created by the dockerfile and solver is a
        :py:class:`conda.core.solve.Solver` instance.

    '''

    if conda_specs is None:
        conda_specs = {}

    files_in_docker_scope = {}

    with open(dockerfile, 'r') as f:
        docker_wd = os.path.dirname(dockerfile)

        line_getter = f

        in_conda = False
        env = 'base'

        while True:
            try:
                line = next(f).split('#')[0].strip()
            except StopIteration:
                break

            args = re.split(r'\s+', line.rstrip('\\').strip())

            # expand arg abbrevs
            args = [CONDA_ARGS.get(a, a) for a in args]

            if args[0].upper() == 'COPY':
                files_in_docker_scope[args[2]] = (
                    os.path.join(docker_wd, args[1]))
            elif (
                    (args[0].upper() == 'RUN')
                    and (args[1].lower() in ['conda', 'source'])
                    and (args[2].lower() == 'activate')):

                env = args[3]

            elif (
                    (args[0].upper() == 'RUN')
                    and (args[1].lower() == 'conda')
                    and (args[2].lower() in ['install', 'create'])):

                conda_spec = args[1:]

                if line.endswith('\\'):
                    in_conda = True
                else:
                    spec = parse_conda_create_command(env, conda_spec)
                    solver = get_conda_solver(
                        prefix=spec['name'],
                        channels=spec.get('channels'),
                        subdirs=spec.get('subdirs'),
                        specs_to_add=spec.get('dependencies'),
                        existing_solver=conda_specs.get(spec['name'], None))

                    conda_specs[spec['name']] = solver

            elif (
                    (args[0].upper() == 'RUN')
                    and (args[1].lower() == 'conda')
                    and (args[2].lower() == 'env')
                    and (args[3].lower() in ['create', 'update'])):

                if '--file' in args:
                    env_file = files_in_docker_scope[
                        args[args.index('--file') + 1]]

                    with open(env_file, 'r') as y:
                        env_spec = yaml.safe_load(y)

                    solver = get_conda_solver(
                        env_file,
                        existing_solver=conda_specs.get(
                            env_spec['name'], None))

                    conda_specs[solver.prefix] = solver

                else:
                    raise ValueError(
                        "I can't parse this line: {}".format(line))

            elif in_conda:
                conda_spec += args

                if not line.endswith('\\'):
                    spec = parse_conda_create_command(env, conda_spec)
                    solver = get_conda_solver(
                        prefix=spec['name'],
                        channels=spec.get('channels'),
                        subdirs=spec.get('subdirs'),
                        specs_to_add=spec.get('dependencies'),
                        existing_solver=conda_specs.get(spec['name'], None))

                    conda_specs[spec['name']] = solver
                    in_conda = False

    return conda_specs

def build_final_envs_for_multiple_docker_files(dockerfiles):
    envs = {}
    for dockerfile in dockerfiles:
        envs.update(get_conda_specs(dockerfile, envs))

    return envs
