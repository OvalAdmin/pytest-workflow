"""All tests for workflow files"""
import hashlib
from pathlib import Path
from typing import List, Tuple, Union

import pytest

from .schema import FileTest


class WorkflowFilesTestCollector(pytest.Collector):
    """Collects all the files related tests"""

    def __init__(self, name: str, parent: pytest.Collector,
                 filetests: List[FileTest],
                 cwd: Union[bytes, str]):
        """
        A WorkflowFilesTestCollector starts all the files-related tests
        :param name: The name of the tests
        :param parent: The collector that started this collector
        :param filetests: A list of `FileTest` which are objects that name
        all the properties of a to be tested file
        :param cwd: The directory relative to which relative file paths will
        be tested.
        """
        self.filetests = filetests
        self.cwd = cwd
        super().__init__(name, parent=parent)

    def collect(self):
        """Starts all file related tests"""

        # Get a list of filepaths
        path_existence_pairs = [(x.path, x.should_exist) for x in
                                self.filetests]

        # Get a list of path and md5 pairs for files where path and md5sum are
        # both defined
        path_md5_pairs = [(x.path, x.md5sum) for x in self.filetests if
                          x.path and x.md5sum]

        return [FilesExistCollector(self.name, self, path_existence_pairs,
                                    self.cwd),
                FilesMd5SumCheckCollector(self.name, self, path_md5_pairs,
                                          self.cwd)]


class FilesExistCollector(pytest.Collector):
    """Spawns tests to check for files existence"""

    def __init__(self, name: str, parent: pytest.Collector,
                 path_existence_pairs: List[Tuple[Path, bool]],
                 cwd: Union[bytes, str]):
        """
        :param name: Name of the test.
        :param parent: Collector that started this test.
        :param path_existence_pairs: A list of paths and whether they should
        exist.
        :param cwd: The directory relative to which relative paths are tested.
        """
        self.path_existence_pairs = path_existence_pairs
        self.cwd = cwd
        super().__init__(name, parent=parent)

    def collect(self):
        """Starts all the file existence tests."""
        for path, should_exist in self.path_existence_pairs:
            yield FileExists(self.name, self, Path(self.cwd) / path,
                             should_exist)


class FileExists(pytest.Item):
    """A pytest file exists test."""

    def __init__(self, name: str, parent: pytest.Collector, filepath: Path,
                 should_exist: bool):
        """
        :param name: Test name
        :param parent: Collector that started this test
        :param filepath: A path to the file
        :param should_exist: Whether the file should exist
        """
        super().__init__(name, parent)
        self.file = filepath
        self.should_exist = should_exist

    def runtest(self):
        assert self.file.exists() == self.should_exist


class FilesMd5SumCheckCollector(pytest.Collector):
    def __init__(self, name: str, parent: pytest.Collector,
                 path_md5_pairs: List[Tuple[Path, str]],
                 cwd: Union[bytes, str]):
        super().__init__(name, parent)
        self.path_md5_pairs = path_md5_pairs
        self.cwd = cwd

    def collect(self):
        for path, md5 in self.path_md5_pairs:
            yield CheckMd5("{0}: check md5sum".format(path), self, path, md5,
                           self.cwd)


class CheckMd5(pytest.Item):
    def __init__(self, name: str, parent: pytest.Collector, filepath: Path,
                 md5sum: str, cwd: Union[bytes, str]):
        super().__init__(name, parent)
        self.filepath = Path(cwd) / filepath
        self.md5sum = md5sum

    def runtest(self):
        assert file_md5sum(self.filepath) == self.md5sum


def file_md5sum(filepath: Path):
    """
    Generates a md5sum for a file. Reads file in blocks to save memory.
    :param filepath: a pathlib. Path to the file
    :return: a md5sum as hexadecimal string.
    """

    hasher = hashlib.md5()
    with filepath.open('rb') as f:  # Read the file in bytes
        # Hardcode the blocksize at 8192 bytes here.
        # This can be changed or made variable when the requirements compel us
        # to do so.
        for block in iter(lambda: f.read(8192), b''):
            hasher.update(block)
    return hasher.hexdigest()