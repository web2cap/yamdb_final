import os
import sys

from os.path import abspath, dirname, join

from django.utils.version import get_version

root_dir = dirname(dirname(abspath(__file__)))
# root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir_content = os.listdir(BASE_DIR)
PROJECT_DIR_NAME = 'api_yamdb'

sys.path.append(root_dir)
infra_dir_path = join(root_dir, 'infra')




# check that the folder with the project is in the root of the repository
if (
        PROJECT_DIR_NAME not in root_dir_content
        or not os.path.isdir(os.path.join(BASE_DIR, PROJECT_DIR_NAME))
):
    assert False, (
        f'In `{BASE_DIR}` project folder not found `{PROJECT_DIR_NAME}`. '
        f'Make sure you have the correct project structure.'
    )

MANAGE_PATH = os.path.join(BASE_DIR, PROJECT_DIR_NAME)
project_dir_content = os.listdir(MANAGE_PATH)
FILENAME = 'manage.py'
# check that the project structure is correct and manage.py is in place
if FILENAME not in project_dir_content:
    assert False, (
        f'In `{MANAGE_PATH}` not found file `{FILENAME}`. '
        f'Make sure you have the correct project structure.'
    )

assert get_version() < '3.0.0', 'Please use the Django version < 3.0.0'

pytest_plugins = [
    'tests.fixtures.fixture_user',
]
