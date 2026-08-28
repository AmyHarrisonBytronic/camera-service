import pytest
import yaml

from dependencies import loadConfig


@pytest.fixture(autouse=True)
def restore_override():
    """set_config_path is process-global; never leak it between tests."""
    yield
    loadConfig.set_config_path(None)


@pytest.fixture
def config_file(tmp_path):
    def write(data):
        path = tmp_path / "config.yaml"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        loadConfig.set_config_path(path)
        return path

    return write


def test_set_config_path_overrides_the_bundled_config(config_file):
    # this is the hook service-orchestrator drives via `main.py --config <path>`
    config_file({"camera": {"camera_type": "flir"}})

    assert loadConfig.return_config_value("camera.camera_type") == "flir"


def test_set_config_path_none_restores_the_local_default(config_file):
    config_file({"camera": {"camera_type": "flir"}})
    loadConfig.set_config_path(None)

    # back to the config.yaml shipped next to loadConfig.py
    assert loadConfig.get_config() != {"camera": {"camera_type": "flir"}}


def test_return_config_value_walks_dotted_paths(config_file):
    config_file({"archiving": {"archive_directory": "D:/images", "nested": {"deep": 1}}})

    assert loadConfig.return_config_value("archiving.archive_directory") == "D:/images"
    assert loadConfig.return_config_value("archiving.nested.deep") == 1


def test_return_config_value_raises_on_missing_and_empty(config_file):
    config_file({"camera": {"camera_type": "gige"}})

    with pytest.raises(KeyError):
        loadConfig.return_config_value("camera.does_not_exist")
    with pytest.raises(KeyError):
        loadConfig.return_config_value("no_such_section.key")
    with pytest.raises(ValueError):
        loadConfig.return_config_value("")


def test_return_config_value_raises_when_walking_through_a_scalar(config_file):
    config_file({"camera": {"camera_type": "gige"}})

    # camera_type is a string, so it has no ".foo" beneath it
    with pytest.raises(KeyError):
        loadConfig.return_config_value("camera.camera_type.foo")


def test_get_section_returns_empty_for_missing_or_non_mapping(config_file):
    config_file({"camera": {"camera_type": "gige"}, "scalar": 3})

    assert loadConfig.get_section("camera") == {"camera_type": "gige"}
    assert loadConfig.get_section("absent") == {}
    assert loadConfig.get_section("scalar") == {}
    with pytest.raises(ValueError):
        loadConfig.get_section("")


def test_get_config_returns_empty_when_the_file_is_missing(tmp_path):
    loadConfig.set_config_path(tmp_path / "absent.yaml")

    assert loadConfig.get_config() == {}
