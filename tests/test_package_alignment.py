
<<<<<<< HEAD
import os
import re
=======
from __future__ import absolute_import

import os
import re
import sys
>>>>>>> dev
import pprint
import conda.core.solve
import pytest

<<<<<<< HEAD
PKG_ROOT = os.path.dirname(os.path.dirname(__file__))

IMAGES_TO_CHECK = [
    'notebook',
    'worker',
    'octave-worker',
    ]

PAIRINGS = {
    'notebook': {
        'base': ['worker'],
        'octave': ['octave-worker'],
    },
}

CONDA_ARGS = {
    'n': 'name',
    'p': 'prefix',
    'c': 'channel',
    'S': 'satisfied-skip-solve',
    'm': 'mkdir',
    'C': 'use-index-cache',
    'k': 'insecure',
    'd': 'dry-run',
    'q': 'quiet',
    'v': 'verbose',
    'y': 'yes'}

def get_conda_specs(dockerfile):
    with open(dockerfile, 'r') as f:
        conda_specs = []

        line_getter = f

        in_conda = False
        env = 'base'

        while True:
            try:
                line = next(f).split('#')[0].strip()
            except StopIteration:
                break

            args = re.split(r'\s+', line.rstrip('\\').strip())

            if (
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
                    conda_specs.append((env, conda_spec))

            elif in_conda:
                conda_spec += args

                if not line.endswith('\\'):
                    conda_specs.append((env, conda_spec))
                    in_conda = False

    return conda_specs

def parse_conda_create_command(env, args):
    if args[0].strip().lower() != 'conda':
        return ('invalid', args)

    chaffe = ['conda', 'install', 'update', 'create', '-y', '--yes']
    install_args = [a for a in args if a.lower() not in chaffe]
    if len(install_args) == 1 and install_args[0].split('=')[0] == 'conda':
        return {'upgrade': tuple(install_args[0].strip('"\'').split('='))}

    spec = {'packages': {}}

    get_install_args = iter(install_args)

    while True:
        try:
            arg = next(get_install_args)
        except StopIteration:
            break

        if arg.startswith('-'):
            a = arg.strip('-')
            spec[CONDA_ARGS.get(a, a)] = next(get_install_args)

        else:
            pkgver = arg.strip('"\'').split('=')
            if len(pkgver) == 1:
                pkgver.append(None)
            spec['packages'].update({pkgver[0]: pkgver[1]})

    spec['name'] = spec.get('name', env)
    spec['channel'] = spec.get('channel', 'defaults')

    return spec

def assert_pairing_match(env, base, penv, pairs):
    for base_spec in base:
        for pkg, ver in base_spec['packages'].items():
            for pair in pairs:
                if pkg in pair.get('packages', {}):
                    pair_ver = pair['packages'][pkg]
                    test = (ver == pair_ver)
                    msg = (
                        'Package versions mis-aligned in env {}:{}'
                        '\n\tpackage {}: {} != {}'
                        .format(env, penv, pkg, ver, pair_ver))
                    assert test, msg

def assert_conda_spec_validity(img, spec):
    for img_spec in spec:
        if not 'packages' in img_spec:
            continue

        # for s, cmd in img_spec.items():
        print(
            'Solving {} package spec {} with channel {}'.format(
                img,
                img_spec.get('name', 'base'),
                img_spec.get('channel', 'defaults')))

        solver = conda.core.solve.Solver(
            img_spec.get('name', 'base'),
            channels=[img_spec.get('channel', 'defaults'), 'defaults'],
            specs_to_add=tuple(map(lambda x: '='.join([i for i in x if i is not None]), img_spec['packages'].items())))

        state = solver.solve_final_state()
=======
if os.path.isdir('../maintenance_utilities'):
    sys.path.append('../maintenance_utilities')
elif os.path.isdir('maintenance_utilities'):
    sys.path.append('maintenance_utilities')

import conda_tools

PKG_ROOT = os.path.dirname(os.path.dirname(__file__))

IMAGES_TO_CHECK = {
    'notebook': ['notebook/Dockerfile'],
    'worker': ['worker/Dockerfile'],
    }


PAIRINGS = [
    ('notebook', 'base', 'worker', 'worker'),
]
'''
PAIRINGS

A  list of tuples of (notebook image, notebook env, worker image, worker env)
pairings. For each pairing, all packages will be tested against each other to
ensure we don't have any dependency conflicts.
'''
>>>>>>> dev


@pytest.fixture(scope='module')
def package_spec():
<<<<<<< HEAD
    specs = {}

    for img_name in IMAGES_TO_CHECK:
        files = os.listdir(os.path.join(PKG_ROOT, img_name))
        dockerfiles = [f for f in files if f.startswith('Dockerfile')]
        specs[img_name] = []
        for dockerfile in dockerfiles:
            fp = os.path.join(PKG_ROOT, img_name, dockerfile)
            s = get_conda_specs(fp)
            env_specs = [
                parse_conda_create_command(k, v)
                for (k, v) in get_conda_specs(fp)]

            specs[img_name] += env_specs

    yield specs


@pytest.mark.parametrize('base', PAIRINGS.keys())
def test_package_pairing(package_spec, base):
    pairs = PAIRINGS[base]
    for env, paired in pairs.items():
        for p in paired:
            nb_env = [s for s in package_spec[base] if 'name' in s and s['name'] == env]
            assert_pairing_match(env, nb_env, p, package_spec[p])


@pytest.mark.parametrize('img', IMAGES_TO_CHECK)
def test_package_validity(package_spec, img):
    spec = package_spec[img]
    assert_conda_spec_validity(img, spec)
=======
    '''
    Returns a nested dictionary of images and solved conda environments

    For each image in IMAGES_TO_CHECK, loops over the provided dockerfiles
    used to construct the image, and finds the final conda environments
    created in the dockerfiles. For each environment, the package specs
    are solved using the conda API and what is returned is a dictionary
    of dictionaries of conda solutions, indexed by docker image and then
    conda env within each image.

    This solution is time consuming and catches package specification errors,
    dependency and build conflicts, channel specification errors, and other
    things that can go wrong in the process of specifying environments.

    Once all image environments have been solved, the resulting nested dict
    is yielded as a package spec that can be used in other unit tests, such
    as in tests of notebook:worker env pairings.

    Examples
    --------

    For example, the following test would invoke the package_spec fixture
    when run with pytest, and would loop over all images, all environments in
    each image, and all packages within each environment, and test each to
    ensure that any python versions encountered were greater than version 3.0

    .. code-block:: python

        >>> from distutils.version import LooseVersion

        >>> def test_all_py3k(package_spec):
        ...     for img, envs in package_spec.items():
        ...         for prefix, env in envs.items():
        ...             for package in env:
        ...                 if package.name == 'python':
        ...                     assert LooseVersion(package.version) >= '3.0'
        ...

    '''

    specs = {}

    for img_name, dockerfiles in IMAGES_TO_CHECK.items():
        dockerfiles = [os.path.join(PKG_ROOT, fp) for fp in dockerfiles]
        specs[img_name] = {}

        envs = (
            conda_tools
            .build_final_envs_for_multiple_docker_files(dockerfiles))

        for env, solver in envs.items():
            specs[img_name][env] = solver.solve_final_state()

    yield specs


def assert_pairing_match(base_name, base_spec, paired_name, paired_spec):
    failures = []
    for pkg in base_spec:
        for pair in paired_spec:
            if pkg.name == pair.name:
                if pkg.version != pair.version:
                    failures.append((pkg, pair))

    if len(failures) > 0:
        raise ValueError(
            'Package versions mis-aligned in {} <> {} pairing:\n\t{}'
            .format(
                base_name,
                paired_name,
                '\n\t'.join([
                    'package {}: {} != {}'
                    .format(n.name, n.version, w.version)
                    for n, w in failures]))
        )


@pytest.mark.parametrize('pairing', PAIRINGS)
def test_package_pairing(package_spec, pairing):
    notebook_image, notebook_env, worker_image, worker_env = pairing
    notebook_spec = package_spec[notebook_image][notebook_env]
    worker_spec = package_spec[worker_image][worker_env]

    assert_pairing_match(
        notebook_image + ':' + notebook_env,
        notebook_spec,
        worker_image + ':' + worker_env,
        worker_spec)
>>>>>>> dev
