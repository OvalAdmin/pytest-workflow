# Copyright (C) 2018 Leiden University Medical Center
# This file is part of pytest-workflow
#
# pytest-workflow is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# pytest-workflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with pytest-workflow.  If not, see <https://www.gnu.org/licenses/

import pytest


class GenericTest(pytest.Item):
    """Test that can be used to report a failing or succeeding test
    in the log"""

    def __init__(self, name: str, parent: pytest.Collector, result: bool):
        """
        Create a GenericTest item
        :param name: The name of the test
        :param parent: A pytest Collector from which the test originates
        :param result: Whether the test has succeeded.
        """
        super().__init__(name, parent=parent)
        self.result = result

    def runtest(self):
        assert self.result
