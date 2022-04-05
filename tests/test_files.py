from unittest.mock import Mock
import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from ees_network_drive.configuration import Configuration  # noqa
from ees_network_drive.indexing_rule import IndexingRules  # noqa
from ees_network_drive.files import Files  # noqa
from ees_network_drive.network_drive_client import NetworkDrive  # noqa


CONFIG_FILE = os.path.join(
    os.path.join(os.path.dirname(__file__), "config"),
    "network_drive_connector.yml",
)


def settings():
    """This function loads config from the file and returns it."""
    configuration = Configuration(file_name=CONFIG_FILE)

    logger = logging.getLogger("unit_test_indexing")
    return configuration, logger


def test_recursive_fetch():
    """Test that recursive_fetch recursively fetch folder paths from Network Drives."""
    config, logger = settings()
    network_drive_client = NetworkDrive(config, logger)
    files_obj = Files(logger, config, network_drive_client)
    expected_response = ["dummy/folder1"]
    mock_file1 = Mock(filename=".")
    files_obj.network_drives_client.connect = Mock()
    files_obj.network_drives_client.connect.listPath = Mock(return_value=[mock_file1])
    response = files_obj.recursive_fetch(
        files_obj.network_drives_client.connect, "Users", "dummy/folder1", []
    )
    assert response == expected_response


def test_extract_files():
    """Test that extract_files successfully create dictionary of ids and file details for the files fetched"""
    config, logger = settings()
    network_drive_client = NetworkDrive(config, logger)
    files_obj = Files(logger, config, network_drive_client)
    time_range = {
        "start_time": "2021-12-28T15:14:28Z",
        "end_time": "2022-03-25T15:14:28Z",
    }
    indexing_rule_obj = IndexingRules(config)
    indexing_rule_obj.should_index = Mock(return_value=True)
    expected_response = {
        1: {
            "updated_at": "2021-12-30T15:14:28Z",
            "file_type": ".txt",
            "file_size": 30,
            "created_at": "1975-03-15T03:55:26Z",
            "file_name": "file1.txt",
            "file_path": rf'{os.path.join("dummy", os.path.join("folder1", "file1.txt"))}',
            "web_path": rf'{os.path.join("file://1.2.3.4/Users/dummy", os.path.join("folder1", "file1.txt"))}'
        }
    }
    mock_file1 = Mock(
        isDirectory=False,
        filename="file1.txt",
        last_attr_change_time=1640877268,
        create_time=164087726,
        file_size=30,
        file_id=1,
    )
    files_obj.network_drives_client.connect = Mock()
    files_obj.network_drives_client.connect.listPath = Mock(return_value=[mock_file1])
    response = files_obj.extract_files(
        files_obj.network_drives_client.connect,
        "Users",
        os.path.join("dummy", "folder1"),
        time_range,
        indexing_rule_obj,
    )
    assert response == expected_response


def test_fetch_files():
    """Test that fetch_files successfully fetch files and create documents."""
    mock_response_files = {
        1: {
            "updated_at": "2021-12-30T15:14:28Z",
            "file_type": ".txt",
            "file_size": 30,
            "created_at": "1975-03-15T03:55:26Z",
            "file_name": "file1.txt",
            "file_path": "dummy/folder1/file1.txt",
            "web_path": "file://1.2.3.4/Users/dummy/folder1/file1.txt",
        }
    }
    mock_response_permission = {"allow": "user1", "deny": "user2"}
    mock_response_file_content = "some text"
    expected_response = [
        {
            "id": "1",
            "body": "some text",
            "last_updated": "2021-12-30T15:14:28Z",
            "type": ".txt",
            "size": 30,
            "created_at": "1975-03-15T03:55:26Z",
            "title": "file1.txt",
            "path": "dummy/folder1/file1.txt",
            "url": "file://1.2.3.4/Users/dummy/folder1/file1.txt",
            "_allow_permissions": "user1",
            "_deny_permissions": "user2",
        }
    ]
    config, logger = settings()
    network_drive_client = NetworkDrive(config, logger)
    files_obj = Files(logger, config, network_drive_client)
    files_obj.network_drives_client.connect = Mock()
    files_obj.network_drives_client.connect.close = Mock(return_value=False)
    files_obj.extract_files = Mock(return_value=mock_response_files)
    files_obj.retrieve_permission = Mock(return_value=mock_response_permission)
    files_obj.fetch_file_content = Mock(return_value=mock_response_file_content)
    time_range = {
        "start_time": "2021-12-28T15:14:28Z",
        "end_time": "2022-03-25T15:14:28Z",
    }
    indexing_rule_obj = IndexingRules(config)
    response = files_obj.fetch_files(
        "Users", ["dummy/folder1"], time_range, indexing_rule_obj
    )
    assert response == expected_response
