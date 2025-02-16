import os
import pytest
import yaml
import shutil
from file_manager import (
    load_config,
    folder_scanner,
    file_type_identifier,
    folder_creator,
    file_mover,
    file_compressor,
)


# Fixtures
@pytest.fixture
def temp_folder(tmp_path="data/test_folder"):
    """Create a temporary folder for testing"""
    if not tmp_path:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tmp_path = os.path.join(root_dir, "data", "test_folder")
    return str(tmp_path)


@pytest.fixture
def empty_folder(empty_folder="empty_folder"):
    """Create a empty folder for testing"""
    if not empty_folder:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        empty_folder = os.path.join(root_dir, "data", "empty_folder")
    return str(empty_folder)


@pytest.fixture
def sample_files(temp_folder="data/test_folder"):
    """Create sample files for testing"""
    # Create test files
    files = ["test.pdf", "image.jpg", "document.PNG"]
    for file in files:
        with open(os.path.join(temp_folder, file), "w") as f:
            f.write("test content")
    return files


@pytest.fixture
def config_file(temp_folder="data/test_folder"):
    """Create a temporary config file"""
    config = {
        "file_manager": {
            "file_types": ["PDF", "JPG", "PNG"],
            "compression_method": [{"PDF": "zip"}, {"JPG": "zip"}, {"PNG": "zip"}],
        }
    }
    config_path = os.path.join(temp_folder, "config.yml")
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return config_path


# Tests for load_config
def test_load_config(config_file):
    """Test loading configuration from YAML file"""
    # monkeypatch.chdir(os.path.dirname(config_file))
    config = load_config(config_file)
    assert "file_manager" in config
    assert "file_types" in config["file_manager"]
    assert "PDF" in config["file_manager"]["file_types"]


# Tests for folder_scanner
def test_folder_scanner_with_files(temp_folder, sample_files):
    """Test scanning folder with files"""
    files, exists = folder_scanner(temp_folder)
    assert exists is True
    assert len(files) == len(sample_files) + 1  # +1 for the config.yml file
    assert all(file in files for file in sample_files)


def test_folder_scanner_nonexistent_folder():
    """Test scanning non-existent folder"""
    files, exists = folder_scanner("/nonexistent/folder")
    assert exists is False
    assert len(files) == 0


def test_folder_scanner_empty_folder(empty_folder):
    """Test scanning empty folder"""
    files, exists = folder_scanner(empty_folder)
    assert exists is False
    assert len(files) == 0


# Tests for file_type_identifier
def test_file_type_identifier_valid_files():
    """Test identifying valid file types"""
    test_cases = [
        ("document.PDF", ("PDF", True)),
        ("image.jpg", ("JPG", True)),
        ("test.PNG", ("PNG", True)),
    ]
    for input_path, expected in test_cases:
        assert file_type_identifier(input_path) == expected


def test_file_type_identifier_invalid_files():
    """Test identifying invalid file types"""
    test_cases = [
        ("", ("", False)),
        (None, ("", False)),
        ("file_without_extension", ("", False)),
        (".hidden", ("", False)),
    ]
    for input_path, expected in test_cases:
        assert file_type_identifier(input_path) == expected


# Tests for folder_creator
def test_folder_creator_single_type(temp_folder):
    """Test creating folder for single file type"""
    assert folder_creator(temp_folder, "PDF") is True
    assert os.path.exists(os.path.join(temp_folder, "PDF"))


def test_folder_creator_all_types(temp_folder, config_file):
    """Test creating folders for all file types"""
    assert folder_creator(temp_folder) is True
    config = load_config()
    for file_type in config["file_manager"]["file_types"]:
        assert os.path.exists(os.path.join(temp_folder, file_type))


def test_folder_creator_existing_folders(temp_folder):
    """Test creating folders that already exist"""
    os.makedirs(os.path.join(temp_folder, "PDF"), exist_ok=True)
    assert folder_creator(temp_folder, "PDF") is False


# Tests for file_mover
def test_file_mover_success(temp_folder, sample_files):
    """Test successful file moving"""
    source_file = os.path.join(temp_folder, "test.pdf")
    new_path, success = file_mover(source_file, temp_folder, "PDF")
    assert success is True
    assert os.path.exists(new_path)
    assert not os.path.exists(source_file)


def test_file_mover_nonexistent_file(temp_folder):
    """Test moving non-existent file"""
    new_path, success = file_mover(
        os.path.join(temp_folder, "nonexistent.pdf"), temp_folder, "PDF"
    )
    assert success is False
    assert new_path == ""


# Tests for file_compressor
def test_file_compressor_success(temp_folder, sample_files, config_file):
    """Test successful file compression"""
    test_file = os.path.join(temp_folder, "PDF", "test.pdf")
    os.makedirs(os.path.join(temp_folder, "PDF"), exist_ok=True)
    shutil.copy(os.path.join(temp_folder, "test.pdf"), test_file)

    compressed_path, success = file_compressor(test_file)
    assert success is True
    assert compressed_path.endswith("_compressed.zip")
    assert os.path.exists(compressed_path)


def test_file_compressor_nonexistent_file(temp_folder):
    """Test compressing non-existent file"""
    compressed_path, success = file_compressor(
        os.path.join(temp_folder, "nonexistent.pdf")
    )
    assert success is False
    assert compressed_path == ""


def test_file_compressor_unsupported_type(temp_folder, sample_files, config_file):
    """Test compressing file with unsupported type"""
    # Create a file type not in compression methods
    test_file = os.path.join(temp_folder, "UNSUPPORTED", "test.txt")
    os.makedirs(os.path.join(temp_folder, "UNSUPPORTED"), exist_ok=True)
    with open(test_file, "w") as f:
        f.write("test content")

    compressed_path, success = file_compressor(test_file)
    assert success is False
    assert compressed_path == ""
