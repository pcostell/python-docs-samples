import os
import fnmatch

import nox

REPO_TOOLS_REQ =\
    'git+https://github.com/GoogleCloudPlatform/python-repo-tools.git'


def session_lint(session):
    session.install('flake8', 'flake8-import-order')
    session.run(
        'flake8', '--builtin=gettext', '--max-complexity=10',
        '--import-order-style=google',
        '--exclude',
        'container_engine/django_tutorial/polls/migrations/*,.nox,.cache,env',
        *(session.posargs or ['.']))


def list_files(folder, pattern):
    for root, folders, files in os.walk(folder):
        for filename in files:
            if fnmatch.fnmatch(filename, pattern):
                yield os.path.join(root, filename)


def session_reqcheck(session):
    session.install(REPO_TOOLS_REQ)

    if 'update' in session.posargs:
        command = 'update-requirements'
    else:
        command = 'check-requirements'

    for reqfile in list_files('.', 'requirements*.txt'):
        session.run('gcprepotools', command, reqfile)


COMMON_PYTEST_ARGS = [
    '-x', '--no-success-flaky-report', '--cov', '--cov-config',
    '.coveragerc', '--cov-append', '--cov-report=']

SAMPLES = [
    'bigquery/api',
    'blog/introduction_to_data_models_in_cloud_datastore',
    'cloud_logging/api',
    'compute/api',
    'compute/autoscaler/demo',
    'datastore/api',
    'managed_vms/cloudsql',
    'managed_vms/datastore',
    'managed_vms/disk',
    'managed_vms/extending_runtime',
    'managed_vms/hello_world',
    'managed_vms/hello_world_compat',
    'managed_vms/memcache',
    'managed_vms/pubsub',
    'managed_vms/static_files',
    'managed_vms/storage',
    'monitoring/api',
    'storage/api',
]


@nox.parametrize('interpreter', ['python2.7', 'python3.4'])
@nox.parametrize('sample', SAMPLES)
def session_tests(session, interpreter, sample):
    session.interpreter = interpreter
    session.install(REPO_TOOLS_REQ)
    session.install('-r', 'requirements-{}-dev.txt'.format(interpreter))
    session.run(
        'py.test', sample, '-m not slow and not flaky',
        *COMMON_PYTEST_ARGS)
