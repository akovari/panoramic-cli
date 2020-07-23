import tempfile

import pytest
import yaml

from panoramic.cli.config.auth import get_client_id, get_client_secret
from panoramic.cli.errors import (
    InvalidYamlFile,
    MissingConfigFileException,
    MissingValueException,
)
from panoramic.cli.local.file_utils import Paths


def test_no_config_file(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirname:
        monkeypatch.setenv('HOME', tmpdirname)

        with pytest.raises(MissingConfigFileException):
            get_client_id()

        with pytest.raises(MissingConfigFileException):
            get_client_secret()


def test_invalid_config_file(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirname:
        monkeypatch.setenv('HOME', tmpdirname)
        Paths.config_dir().mkdir()

        with open(Paths.config_file(), 'w') as f:
            f.write('client_id: some_value\nclient_secret slug_but_missing_colon\n')

        with pytest.raises(InvalidYamlFile):
            assert get_client_id()

        with pytest.raises(InvalidYamlFile):
            assert get_client_secret()


def test_missing_value_config_file(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirname:
        monkeypatch.setenv('HOME', tmpdirname)
        Paths.config_dir().mkdir()

        with open(Paths.config_file(), 'w') as f:
            f.write(yaml.dump(dict(client_secret='some_random_value')))

        with pytest.raises(MissingValueException):
            get_client_id()

    with tempfile.TemporaryDirectory() as tmpdirname:
        monkeypatch.setenv('HOME', tmpdirname)
        Paths.config_dir().mkdir()

        with open(Paths.config_file(), 'w') as f:
            f.write(yaml.dump(dict(client_id='another_random_value')))

        with pytest.raises(MissingValueException):
            get_client_secret()


def test_config_file(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirname:
        monkeypatch.setenv('HOME', tmpdirname)
        Paths.config_dir().mkdir()

        with open(Paths.config_file(), 'w') as f:
            f.write(yaml.dump(dict(client_id='some_random_id', client_secret='some_random_secret')))

        assert get_client_id() == 'some_random_id'
        assert get_client_secret() == 'some_random_secret'
