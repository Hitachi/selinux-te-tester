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

import os

def check_permission(permission, body, error=Exception ):
  ok = False
  err = None
  rtn = None
  try:
    rtn = body()
  except error as e:
    ok = False
    err = e
  else:
    ok = True
    err = None
  result = {
    "permission": permission,
    "ok": ok,
    "err": err
  }
  return rtn, result  

def check_open(path, mode="r"):
  f = None
  f, result = check_permission("open({0})".format(mode), lambda: open(path, mode))
  #f, result = check_permission("open({0})".format(mode), lambda: os.open(path, os.O_RDONLY )
  return (f, result)  

def check_close(f):
  _, result = check_permission("close", lambda: f.close())
  return (f, result)  

def check_read(f):
  #_, result = check_permission("read", lambda: os.read(f.fileno(), 1))
  _, result = check_permission("read", lambda: f.read(1))
  return (f, result)  

def check_getattr(path):
  st, result = check_permission("getattr", lambda: os.lstat(path))
  return st, result

import os, stat
def check_file(path):
  results = [] 

  st, result = check_getattr(path)
  results.append(result)

  f, result = check_open(path)
  results.append(result)

  if not f is None:
    f, result = check_read(f)
    results.append(result)
      
  if not f is None:
    f, result = check_close(f)
    results.append(result)
  
  return {
    "target": path,
    "type": "file",
    "results": results
  }

def check_files(data):
  for item in list_files(data):
    path = item["path"]
    yield check_file(path)

def list_files(data):
  for d in data["dirs"]:
    if d.get("r", False):
      for (root, dirs, files) in os.walk(d["path"]):
        for file in files:
          path = os.path.join(root, file)
          is_file = False
          try:
            st = os.lstat(path)
            mode = st[stat.ST_MODE]
            is_file = stat.S_ISREG(mode)
          except:
            pass
          if is_file:
            yield {"path": path}
  for file in data["files"]:
    yield file


def list_port(data):
  for item in data["ports"]:
    if "start" in item:
      start = item["start"]
      end = item["end"]
      for port in range(start, end):
        yield port
    else:
      port = item["port"]
      yield port

import socket
def check_ports(data):
  for port in list_port(data):
    s = socket.socket()
    _, result = check_permission("bind", lambda: s.bind(('', port)))
    s.close()
    yield { "target": port , "type": "port", "results": [result] }

def check_access(data):
  for report in check_files(data):
    yield report
  for report in check_ports(data):
    yield report

import sys
def print_report(report):
  csv_writer = csv.writer(sys.stdout)
  target = report["target"]
  for result in report["results"]:
    state = ""
    msg = ""
    if result["ok"]:
      state = "OK"
      msg = "-"
    else:
      state = "NG"
      msg = result["err"]
    csv_writer.writerow([
      state, result["permission"], report["type"], target, msg
    ])  

import csv
def load_data(path):
  dirs = []
  files = []
  ports = []
  
  with open(path) as f:
    reader = csv.reader(f)
    for row in reader:
      row = [ item.strip() for item in row]
      type = row[0]
      if type == "dir":
        dirs.append({
          "path": row[1],
          "r": True
        })
      elif type == "file":
        files.append({
          "path": row[1]
        })
      elif type == "port":
        target = row[1]
        if "-" in target:
          start, end = target.split("-")
          start = int(start)
          end = int(end)
          ports.append({
            "start": start,
            "end": end
          })
        else:
          ports.append({
            "port": int(target)
          })
  return {
    "dirs": dirs,
    "files": files,
    "ports": ports
  }
          

if __name__ == "__main__":
  import sys
  args = sys.argv
  DATA = load_data(args[1])

  for report in check_access(DATA):
    print_report(report)
