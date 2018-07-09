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

import subprocess
import shlex
def split(cmd):
  return shlex.split(cmd) 

def execute(cmd, params={}):
  if isinstance(cmd, basestring):
    cmd = split(cmd)
  return subprocess.call(cmd, **params)

def silent_execute(cmd, params={}):
  devnull = open('/dev/null', 'w')
  params["stdout"] = devnull
  params["stderr"] = subprocess.STDOUT
  return execute(cmd, params)

def execute_and_read_lines(cmd):
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  while True:
    line = proc.stdout.readline()
    if line != '':
      yield line
    else:
      return
