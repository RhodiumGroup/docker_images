
from __future__ import absolute_import

import os
import re
import sys
import pprint
import conda.core.solve
import pytest

if os.path.isdir('../maintenance_utilities'):
    sys.path.append('../maintenance_utilities')
elif os.path.isdir('maintenance_utilities'):
    sys.path.append('maintenance_utilities')

import conda_tools

PKG_ROOT = os.path.dirname(os.path.dirname(__file__))

IMAGES_TO_CHECK = {
    'notebook': ['notebook/Dockerfile'],
    'worker': ['worker/Dockerfile'],
    'octave': ['octave-worker/Dockerfile'],
    }


PAIRINGS = [
    ('notebook', 'base', 'worker', 'base'),
    ('notebook', 'base', 'octave-worker', 'base'),
]
'''
PAIRINGS

A  list of tuples of (notebook image, notebook env, worker image, worker env)
pairings. For each pairing, all packages will be tested against each other to
ensure we don't have any dependency conflicts.

'''


@pytest.fixture(scope='module')
def package_spec():
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
