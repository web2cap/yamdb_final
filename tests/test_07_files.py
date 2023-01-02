import os

from .conftest import MANAGE_PATH, project_dir_content, root_dir_content

# We check that the models are not in the folders of the API application
api_path = os.path.join(MANAGE_PATH, 'api')
if 'api' in project_dir_content and os.path.isdir(api_path):
    api_dir_content = os.listdir(api_path)
    assert 'models.py' not in api_dir_content, (
        f'In the Directory `{api_path}` there should not be a file with models.'
        'They are not needed in this application. '
    )
else:
    assert False, f'No application `API` in the folder {MANAGE_PATH} '


# test .md
default_md = '# api_yamdb\napi_yamdb\n'
filename = 'README.md'
assert filename in root_dir_content, (
    f'In the root of the project, the file {filename} `'
)

with open(filename, 'r') as f:
    file = f.read()
    assert file != default_md, (
        f'Do not forget to arrange `{filename}` '
    )
