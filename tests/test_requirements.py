import os

from django.conf import settings


class TestRequirements:

    def test_requirements(self):
        try:
            with open(f'{os.path.join(settings.BASE_DIR, "requirements.txt")}', 'r') as f:
                requirements = f.read()
        except FileNotFoundError:
            assert False, 'Check that you have added the requirements.txt file'

        assert 'gunicorn' in requirements, 'Check that you have added gunicorn to your requirements.txt file'
        assert 'django' in requirements, 'Check that you have added django to your requirements.txt file'
        assert 'pytest-django' in requirements, 'Check that you have added pytest-django to your requirements.txt file'
