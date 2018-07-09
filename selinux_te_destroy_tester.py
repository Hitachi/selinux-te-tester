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

import argparse
import subprocess
import os
import commands
import sys

from lib.resource import load_template
from lib.selinux import Sepolicy, user_selinux_context
from selinux_te_tester import te_file
from lib.process import execute_and_read_lines, silent_execute

import string
import random
import datetime

def load_data(path):
  with open(path) as f:
    return [ line.strip() for line in f.readlines()]

def file_name(n=10):
  c = string.ascii_lowercase + string.ascii_uppercase + string.digits
  number = ''.join([random.choice(c) for i in range(n)])
  now = datetime.datetime.now()
  return "{0:%Y%m%d%H%M%S%f}_{1}".format(now, number)

def list_path(data):
  for path in data:
    yield path

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='SELinux TE Destroy Tester.')
  parser.add_argument('--disabled-uninstall-policy', action='store_true',
                       help='Disabled to uninstall the policy')
  parser.add_argument('domain', help='SELinux domain applied to the test process.')
  parser.add_argument('config', help='Config file.')
  args = parser.parse_args()

  target_domain = args.domain
  config_path = args.config

  DATA = load_data(config_path)

  module_dir = "module"
  module_name = "te-tester-write"
  work_dir = "work"
  policy = Sepolicy(module_name)
  policy.set_disabled_uninstall(args.disabled_uninstall_policy)

  _, user_role, user_domain, _ = user_selinux_context()

  if not os.path.isdir(module_dir):
    os.mkdir(module_dir) 

  if not os.path.isdir(work_dir):
    os.mkdir(work_dir) 

  map = {}
  for path in list_path(DATA):
    cmd = "ls -Z {0}".format(path)
    output = commands.getoutput(cmd)
    label = output.split(" ")[3]
    type = label.split(":")[2]
    dummy_file_name = file_name()
    dummy_path = os.path.abspath(os.path.join(work_dir, dummy_file_name))
    policy.append_fc_with(dummy_path, type)
    with open(dummy_path, "w") as f:
      f.write("Dummy File")
    map[path] = dummy_path

  te_content = te_file(module_name, user_role, user_domain, target_domain)
  policy.append_te(te_content)

  cmd_path = "script/destroy.py"
  cmd_path = os.path.abspath(cmd_path)
  policy.append_fc_with(cmd_path, "{}_exec_t".format(module_name))
  policy.append_fc_with(os.path.abspath("script/access.py"), 
                            "{}_config_t".format(module_name))
  with policy.install_customize_policy(module_dir, user_domain):
    for path in list_path(DATA):
      dummy_path = map[path]
      for line in execute_and_read_lines("./script/destroy.py {0} {1}".format(dummy_path, path)):
        sys.stdout.write(line)
      #subprocess.call("./script/destroy.py {0} {1}".format(dummy_path, path), shell=True)

  for path in list_path(DATA):
    dummy_path = map[path]
    if os.path.isfile(dummy_path):
      silent_execute(["chcon", "-t", "user_tmp_t", dummy_path])
      os.remove(dummy_path)

  if args.disabled_uninstall_policy:
    sys.stderr.write("[WARNING]The policy module hasn't be uninstalled. You MUST run 'semodule -r {0}'.\n".format(module_name) )

