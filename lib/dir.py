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

import os
class WithDir:
  def __init__(self, target_dir):
    self.target_dir = target_dir

  def __enter__(self):
    self.original_dir = os.getcwd()
    os.chdir(self.target_dir)
    return self

  def __exit__(self, exception_type, exception_value, traceback):
    os.chdir(self.original_dir)

def chdir(dir):
  return WithDir(dir)