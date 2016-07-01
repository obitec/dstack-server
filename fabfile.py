import json

from fabric.api import env, local, run, cd
from fabric.contrib.project import upload_project
from fabric.operations import sudo
from fabric.main import load_settings
import os

settings = load_settings('.env')
if not settings:
    raise RuntimeError('.env file is needed')
env.update(settings)
env.use_ssh_config = True


def machine(cmd: str = '--help', dry_run: bool = False, capture: bool = False):
    """ Wrapper for docker-machine

    :param cmd: The docker-machine command to execute, see --help for details
    :param dry_run: If True, does not execute command, only print it
    :param capture: Passed on to local
    :return:
    """
    if not dry_run:
        return local('docker-machine {cmd}'.format(cmd=cmd), capture=capture)
    else:
        print('docker-machine {cmd}'.format(cmd=cmd))


def create(driver: str = 'virtualbox', name: str = 'default', dry_run=False):
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
    machine(cmd=command, dry_run=dry_run)


def status(name: str = 'default'):
    """ Attempts to parse docker-machine ip, config and status to get
    the path to the key file and the ip address.

    :param name:
    :return:
    """
    # ip = machine('ip {name}'.format(name=name), capture=True)
    # status = machine('status {name}'.format(name=name), capture=True)
    # [3] is tlskey and [1] is the path
    # key_file = [i.strip('-').replace('"', '').split('=') for i in config.split('\n')][3][1]


def create_ssh_config(name: str = 'default', dry_run: bool = False,):
    """ Create ssh config entry from docker-machine inspect

    """
    config = machine('inspect {name}'.format(name=name), capture=True)
    config = json.loads(config)
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


def configure_server(name: str = 'default', ):
    machine('scp setup.sh {name}:/root/setup.sh'.format(**locals()))
    machine('scp docker-compose.yml {name}:/root/docker-compose.yml'.format(**locals()))
    machine('scp {name}.env {name}:/root/.env'.format(**locals()))
    machine('ssh {name} chmod 700 setup.sh'.format(**locals()))
    machine('ssh {name} ./setup.sh'.format(**locals()))
    #local('bw apply node1')


def install_image_factory():
    # run('docker pull obitec/wheel-factory')
    with cd('/srv/build/'):
        run('wget https://github.com/obitec/wheel-factory/archive/master.tar.gz')
        run('tar -zxvf master.tar.gz --strip=1')
        run('rm master.tar.gz')
