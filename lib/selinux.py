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

from process import silent_execute
from dir import chdir

def seplicy_generate_customize(target_domain, module_name):
  cmd = "sepolicy generate --customize -d {0} -n {1}"
  cmd = cmd.format(target_domain, module_name)
  silent_execute(cmd, {"env": {"LANG":"C"} })

def update_file(module_name, ext, content):
  file_name = "{0}.{1}".format(module_name, ext)
  with open(file_name, "a") as file:
    file.write(content)

def update_te_file(module_name, content):
  update_file(module_name, "te", content)

def update_fc_file(module_name, content):
  update_file(module_name, "fc", content)

def content_of_fc(path, type):
  return "{0}\t\tgen_context(system_u:object_r:{1},s0)".format(path, type)

def exec_setup(module_name):
  setup_cmd = "./{0}.sh".format(module_name)
  return_code = silent_execute(setup_cmd)
  if return_code != 0:
     raise RuntimeError("Setup script raise error.") 


def install_customize_policy(module_dir, module_name, target_domain, te, fc):
  with chdir(module_dir) as dir:
    seplicy_generate_customize(target_domain, module_name)
    update_te_file(module_name, te)
    update_fc_file(module_name, fc)
    exec_setup(module_name)

def restorecon(path):
  cmd = "restorecon {0}".format(path)
  silent_execute(cmd)

def restorecon_all(paths):
  for path in paths:
    restorecon(path)

def chcon(path, type):
  cmd = ["chcon", "-t", type, path]
  silent_execute(cmd)

import commands
def user_selinux_context():
  cmd = "id -Z"
  output = commands.getoutput(cmd)
  user, role, domain = output.split(':')[0:3]
  level = ":".join(output.split(':')[3:])
  return user, role, domain, level

class Sepolicy:
  def __init__(self, module_name):
    self.module_name = module_name
    self.te_content = ""
    self.fc_content = ""
    self.fc_paths = []
    self.chcon_targets = []
    self.disabled_uninstall = False
  
  def set_disabled_uninstall(self, disabled):
    self.disabled_uninstall = disabled

  def append_te(self, content):
    self.te_content += content + "\n"
  
  def append_fc_with(self, path, type):
    self.fc_paths.append(path)
    #content = content_of_fc(path, type)
    #self.fc_content += content + "\n"
    self.chcon_targets.append((path, type))

  def install_customize_policy(self, module_dir, target_domain):
    install_customize_policy(module_dir, self.module_name,
            target_domain, self.te_content, self.fc_content)
    #restorecon_all(self.fc_paths)
    for path, type in self.chcon_targets:
      chcon(path, type)
    return self.With(self)
  
  def uninstall(self):
    silent_execute("semodule -r {0}".format(self.module_name))
    restorecon_all(self.fc_paths)

  class With:
    def __init__(self, outer):
      self.outer = outer

    def __enter__(self):
      pass

    def __exit__(self, exception_type, exception_value, traceback):
      if not self.outer.disabled_uninstall:
        self.outer.uninstall()

