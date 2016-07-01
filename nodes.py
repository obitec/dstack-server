import os

nodes = {
    'node1': {
        'hostname': os.environ.get('django_hosts', 'gauseng.apps'),
        'bundles': (
            "django_server",
        ),
    },
}
