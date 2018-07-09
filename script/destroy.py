#!/bin/python
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

from access import check_permission, check_open, check_close, print_report
import os
def check_write(f):
  _, result = check_permission("write", lambda: f.write("a"))
  return (f, result)  

def check_delete(path):
  _, result = check_permission("delete", lambda: os.remove(path) )
  return None, result

if __name__ == "__main__":
  import sys
  args = sys.argv
  path = args[1]
  real_path = args[2]

  results = []

  f, result = check_open(path, mode="w")
  results.append(result)
  if not f is None:
    f, result = check_write(f)
    results.append(result)    
  if not f is None:
    f, result = check_close(f)
    results.append(result)
  _, result = check_delete(path)
  results.append(result)

  report = {
    "target": real_path,
    "type": "file",
    "results": results
  }

  print_report(report)