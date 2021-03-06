import json
#from fabric.api import env, local, run, cd
#from fabric.operations import sudo
#from fabric.main import load_settings
import os
import invoke
from invoke import run, task, env
from invoke.util import cd, contextmanager
from dotenv import load_dotenv
from os import environ as env

# settings = load_settings('.env')
# if not settings:
#     raise RuntimeError('.env file is needed')
# env.update(settings)
# env.use_ssh_config = True

load_dotenv('.env')


@task
def machine(ctx, cmd: str = '--help', dry_run: bool = False, capture: bool = False):
    """ Wrapper for docker-machine

    :param cmd: The docker-machine command to execute, see --help for details
    :param dry_run: If True, does not execute command, only print it
    :param capture: Passed on to local
    :return:
    """
    if not dry_run:
        return run('docker-machine {cmd}'.format(cmd=cmd), capture=capture)
    else:
        print('docker-machine {cmd}'.format(cmd=cmd))


@task
def create(ctx, driver: str = 'virtualbox', name: str = 'default', dry_run=False):
    """Create a docker machine
    Automatically uses key and value pairs from .env

    :param driver:
    :param name:
    :param dry_run:
    :return:
    """
    template = 'create --driver {driver} {config} {name}'

    config = ' '.join(['--{key}={value}'.format(
        key=k, value=v) for k, v in env.items() if k.startswith(driver + '-')])

    command = template.format(driver=driver, config=config, name=name)
    machine(ctx, cmd=command, dry_run=dry_run)


@task
def status(ctx, name: str = 'default'):
    """ Attempts to parse docker-machine ip, config and status to get
    the path to the key file and the ip address.

    :param name:
    :return:
    """
    print('Everything is awesome!!')
    ip = machine(ctx, 'ip {name}'.format(name=name), capture=True)
    status = machine(ctx, 'status {name}'.format(name=name), capture=True)
    # [3] is tlskey and [1] is the path
    key_file = [i.strip('-').replace('"', '').split('=') for i in config.split('\n')][3][1]
    print(key_file)


@task
def create_ssh_config(ctx, name: str = 'default', dry_run: bool = False,):
    """ Create ssh config entry from docker-machine inspect

    """
    if not dry_run:
        config = machine(ctx, 'inspect {name}'.format(name=name), capture=True)
        config = json.loads(config)
    else:
        config = {
            'Driver': {
                'MachineName': name,
                'IPAddress': '0.0.0.0',
                'SSHPort': 22,
                'SSHUser': 'root',
                'SSHKeyPath': '~/.ssh/id_rsa'
            }
        }

    home = os.path.expanduser('~')

    ssh_config = """
    Host {MachineName}
        HostName {IPAddress}
        Port {SSHPort}
        User {SSHUser}
        IdentityFile {SSHKeyPath}
    """.format(**config['Driver']).replace('    ', '', 1)

    if dry_run:
        print(ssh_config)
        print(os.path.join(home, '.ssh/config'))
    else:
        with open(os.path.join(home, '.ssh/config'), 'a') as f:
            f.write(ssh_config)


@task
def configure_server(ctx, name: str = 'default', dry_run: bool = False):
    machine(ctx, 'scp setup.sh {name}:/root/setup.sh'.format(**locals()), dry_run=dry_run)
    machine(ctx, 'scp docker-compose.yml {name}:/root/docker-compose.yml'.format(**locals()), dry_run=dry_run)
    machine(ctx, 'scp env/{name} {name}:/root/.env'.format(**locals()), dry_run=dry_run)
    machine(ctx, 'ssh {name} chmod 700 setup.sh'.format(**locals()), dry_run=dry_run)
    machine(ctx, 'ssh {name} ./setup.sh'.format(**locals()), dry_run=dry_run)
    #local('bw apply node1')


@task
def do_it(ctx, name: str = 'default', driver: str = 'digitalocean', dry_run: bool = False):
    create(ctx, name=name, driver=driver, dry_run=dry_run)
    configure_server(ctx, name=name, dry_run=dry_run)
    create_ssh_config(ctx, name=name, dry_run=dry_run)


@task
def install_image_factory(ctx):
    # run('docker pull obitec/wheel-factory')
    with cd('/srv/build/'):
        run('wget https://github.com/obitec/wheel-factory/archive/master.tar.gz')
        run('tar -zxvf master.tar.gz --strip=1')
        run('rm master.tar.gz')
