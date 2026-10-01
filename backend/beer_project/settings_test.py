from .settings import *  # noqa: F401,F403

# Settings used by the test suite. Tests run against an in-memory SQLite database so
# they are fast and do not depend on the MariaDB service being available.
#
#   python manage.py test --settings=beer_project.settings_test

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
