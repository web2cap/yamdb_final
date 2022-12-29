import os
import re

from .conftest import infra_dir_path, root_dir


class TestDockerfileCompose:

    def test_infra_structure(self):
        assert 'infra' in os.listdir(root_dir), (
            f'Check that the {root_dir} path is set to the `infra` folder'
        )
        assert os.path.isdir(infra_dir_path), (
            f'Check that {infra_dir_path} is a folder and not a file'
        )

    def test_docker_compose_file(self):
        try:
            with open(f'{os.path.join(infra_dir_path, "docker-compose.yaml")}', 'r') as f:
                docker_compose = f.read()
        except FileNotFoundError:
            assert False, f'Check that the `docker-compose.yaml` file has been added to the {infra_dir_path} directory`'

        assert re.search(r'image:\s+postgres:', docker_compose), (
            'Check that the postgres:latest image is added to the docker-compose.yaml file'
        )
        assert re.search(r'image:\s+([a-zA-Z0-9]+)\/([a-zA-Z0-9_\.])+(\:[a-zA-Z0-9_-]+)?', docker_compose), (
            'Make sure you add the container build from your DockerHub image to the docker-compose.yaml file'
        )
