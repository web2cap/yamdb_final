import os
import re

from .conftest import root_dir


class TestReadme:

    def test_readme(self):
        try:
            with open(f'{os.path.join(root_dir, "README.md")}', 'r', encoding='utf-8') as f:
                readme = f.read()
        except FileNotFoundError:
            assert False, 'Check that you have added the README.md file'

        re_str = (
            r'https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+'
            r'\/(actions\/)?workflows\/[-a-zA-Z0-9._+]+\/badge\.svg'
        )

        assert re.search(re_str, readme), 'Make sure you have added the workflow status badge to the README.md file'
