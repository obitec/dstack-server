groups = {
    "docker": {
        "gid": 1102,
    },
}

users = {
    "canary": {
        "groups": ["sudo", "docker"],
        "home": "/home/canary",
        # "password_hash": "$6$abcdef$ghijklmnopqrstuvwxyz",
        "shell": "/bin/bash",
        "uid": 1101,
    },
}

pkg_apt = {
    "tree": {
        "installed": True,
    },
    "htop": {
        "installed": True,
    },
    "vim": {
        "installed": True,
    },
}

actions = {
    'install_compose': {
        'command': "curl -L https://github.com/docker/compose/releases/download/1.7.1/"
                   "docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose",
    },
    'fix_permission': {
        'command': "chmod +x /usr/local/bin/docker-compose",
        # 'expected_return_code': 0,
    },
}

# pkg_pip = {
#     "docker-compose": {
#         "installed": True,  # default
#         # "version": "1.7.1",  # optional
#     },
#     # "/path/to/virtualenv/foo": {
#     # will install foo in the virtualenv at /path/to/virtualenv
#     # },
# }

files = {
    '/srv/docker-compose.yml': {
        # "mode": "0644",
        # "owner": "canary",
        # "group": "canary",
        'source': "srv/docker-services.yml",
    },
}

directories = {
    '/srv/certs': {},
    '/srv/config': {},
    '/srv/build': {},
    '/srv/apps/default': {},
    '/srv/htdocs': {
        # "mode": "0644",
        # "owner": "canary",
        # "group": "canary",
    }
}
