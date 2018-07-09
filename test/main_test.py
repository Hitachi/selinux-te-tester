# coding: utf-8

# Copyright (C) 2018  Hitachi, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
import commands

class TestTeTester(unittest.TestCase):

    def test_main(self):
        cmd = "python ../selinux_te_tester.py kernel_t sh/testcase.sh"
        actual = commands.getoutput(cmd)
        expected = "kernel_t"
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()