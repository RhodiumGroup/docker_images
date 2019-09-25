
import os
import re
import pprint
import conda.core.solve
import pytest

PKG_ROOT = os.path.dirname(os.path.dirname(__file__))

IMAGES_TO_CHECK = [
    'notebook',
    'worker',
    ]

PAIRINGS = {
    'notebook': {
        'base': ['worker'],
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


@pytest.fixture(scope='module')
def package_spec():
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
