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
import sys

from lib.dir import chdir
from lib.resource import load_template
from lib.selinux import Sepolicy, user_selinux_context
from lib.process import silent_execute, execute_and_read_lines

def te_file(module_name, user_role, user_domain, target_domain):
  path = "template/te.txt"
  path = os.path.abspath(os.path.join(os.path.dirname(__file__), path));
  template = load_template(path, {
    "module": module_name, "user_role": user_role,
    "user_domain": user_domain, "target_domain": target_domain,
  })
  return template



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='SELinux TE Tester.')
  parser.add_argument('--disabled-uninstall-policy', action='store_true',
                       help='Disabled to uninstall the policy')
  parser.add_argument('domain', help='SELinux domain applied to tester.')
  parser.add_argument('tester', help='Test application applied SELinux domain.')
  parser.add_argument('options', nargs='*', help='Options of Test application')
  args = parser.parse_args()

  target_domain = args.domain
  tester = args.tester
  tester = os.path.abspath(tester)
  options = args.options

  _, user_role, user_domain, _ = user_selinux_context()
  module_name = "te-tester"
  module_dir = "module"

  te_content = te_file(module_name, user_role, user_domain, target_domain)

  if not os.path.isdir(module_dir):
    os.mkdir(module_dir) 

  policy = Sepolicy(module_name)
  policy.set_disabled_uninstall(args.disabled_uninstall_policy)

  policy.append_te(te_content)
  policy.append_fc_with(tester, "{0}_exec_t".format(module_name))
  for option in options:
    if os.path.isfile(option):
      option = os.path.abspath(option)
      policy.append_fc_with(option, "{0}_config_t".format(module_name))

  with policy.install_customize_policy(module_dir, user_domain):
    test_cmd = "{0} {1}".format(tester, " ".join(options))
    for line in execute_and_read_lines(test_cmd):
      sys.stdout.write(line)

  if args.disabled_uninstall_policy:
    sys.stderr.write("[WARNING]The policy module hasn't be uninstalled. You MUST run 'semodule -r {0}'.\n".format(module_name) )
