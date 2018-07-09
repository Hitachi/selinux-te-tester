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

def read_all(file_path):
  content = ""
  with open(file_path, "r") as f:
    content = f.read()
  return content

from string import Template
def load_template(path, params):
  template = read_all(path)
  template = Template(template)
  template = template.substitute(params)
  return template