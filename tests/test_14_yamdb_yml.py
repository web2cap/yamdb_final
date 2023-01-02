import os
import re

from .conftest import root_dir


class TestWorkflow:

    def test_workflow(self):
        yamdb_workflow_basename = 'yamdb_workflow'

        yaml = f'{yamdb_workflow_basename}.yaml'
        is_yaml = yaml in os.listdir(root_dir)

        yml = f'{yamdb_workflow_basename}.yml'
        is_yml = yml in os.listdir(root_dir)

        if not is_yaml and not is_yml:
            assert False, (
                f'File with workflow description not found in directory {root_dir} '
                f'{yaml} or {yml}.\n'
            )

        if is_yaml and is_yml:
            assert False, (
                f'There must not be two {yamdb_workflow_basename} files in the {root_dir} directory '
                 'with extensions .yaml and .yml\n'
                 'Remove one of them'
            )

        filename = yaml if is_yaml else yml

        try:
            with open(f'{os.path.join(root_dir, filename)}', 'r') as f:
                yamdb = f.read()
        except FileNotFoundError:
            assert False, f'Check that you have added the file {filename} to the directory {root_dir} for verification'

        assert (
                re.search(r'on:\s*push:\s*branches:\s*-\smaster', yamdb) or
                'on: [push]' in yamdb or
                'on: push' in yamdb
        ), f'Make sure you add a push action to the {filename} file'
        assert 'pytest' in yamdb, f'Check you have added pytest to the {filename} file'
        assert 'appleboy/ssh-action' in yamdb, f'Check that you have added the deployment to the {filename} file'
        assert 'appleboy/telegram-action' in yamdb, (
            f'Check that you have set up sending a telegram message in {filename}'
        )
