import os

nodes = {
    'node1': {
        'hostname': os.environ.get('hosts', 'ngkdb'),
        'bundles': (
            "django_server",
        ),
    },
}
