from pakkenellik.config import Config


def test_config_returns_known_folders_under_project_root() -> None:
    config = Config("/tmp/project")

    assert config.root == "/tmp/project"
    assert config.source == "/tmp/project/data/source"
    assert (
        config.get_processed_file("data.csv") == "/tmp/project/data/processed/data.csv"
    )


def test_config_returns_none_for_unknown_folder_and_url() -> None:
    config = Config("/tmp/project")

    assert config.get_folder("missing") is None
    assert config.get_url("missing") is None
