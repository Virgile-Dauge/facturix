import pytest
from pathlib import Path
import os
import tempfile
import shutil
import zipfile
from datetime import date

from zipper import create_zip, create_zip_batches


@pytest.fixture
def test_dir():
    path = Path(tempfile.mkdtemp())
    yield path
    shutil.rmtree(path)


@pytest.fixture
def file_paths(test_dir):
    file_paths = [test_dir / f'test_file_{i}.txt' for i in range(10)]
    for file_path in file_paths:
        with file_path.open('w') as f:
            f.write("This is a test file.")
    return file_paths


def test_create_zip(test_dir, file_paths):
    zip_path = test_dir / 'test_archive.zip'
    create_zip(zip_path, file_paths)
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipped_files = zipf.namelist()
        assert len(zipped_files) == len(file_paths)
        for file in file_paths:
            assert file.name in zipped_files


def test_create_zip_batches_files_limit(test_dir, file_paths):
    dest_dir = test_dir / 'zips'
    create_zip_batches(file_paths, dest_dir, max_files=2)
    
    zip_files = list(dest_dir.glob('*.zip'))
    assert len(zip_files) == 5  # 10 files with max 2 files per zip

    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            assert len(zipf.namelist()) <= 2


def test_create_zip_batches_size_limit(test_dir, file_paths):
    large_file = test_dir / 'large_file.txt'
    with large_file.open('w') as f:
        f.write('a' * 1024 * 1024 * 10)  # 10 MB

    files = file_paths + [large_file]
    dest_dir = test_dir / 'zips'
    create_zip_batches(files, dest_dir, max_size_mo=5)  # 5 MB size limit

    zip_files = list(dest_dir.glob('*.zip'))
    assert len(zip_files) > 1  # Expect multiple zips due to size limit

    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            zip_size = sum(zinfo.file_size for zinfo in zipf.infolist())
            assert zip_size <= 5 * 1024 * 1024  # size check


def test_create_zip_batches_single_file_large(test_dir):
    large_file = test_dir / 'large_file.txt'
    with large_file.open('w') as f:
        f.write('a' * 1024 * 1024 * 22)  # 22 MB, larger than the max 20 MB size limit

    files = [large_file]
    dest_dir = test_dir / 'zips'
    
    with pytest.raises(ValueError):
        create_zip_batches(files, dest_dir, max_size_mo=20)


def test_create_zip_batches_empty_list(test_dir):
    dest_dir = test_dir / 'zips'
    create_zip_batches([], dest_dir)
    
    zip_files = list(dest_dir.glob('*.zip'))
    assert len(zip_files) == 0  # No zip files should be created
