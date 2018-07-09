# SELinux Type Enforcement Tester

## Concept
It is difficult to verify Type Enforcement with own process because the process does not touch needless places but the verification needs to touch the places.

However now, we have a good idea! A control of Type Enforcement goes along with SELinux domain and type. Therefore, if a program for the verification is executed as a domain which is same with own process, it could be said to done the verification for own process.

## Attention
* You must have a permission which equals SELinux managers to install policies.
* Is a SELinux mode on your environment set to Enforce? If Permissive, the verification is unable.
* The tool will spend about 30 sec for policy install before an execution of the velification and 10 sec for uninstall after the velification.
* Uninstalling the policy, audit2allow and others don't work. 
* If you need to not uninstall the policy, set --disabled-uninstall-policy option to the first argument. You must uninstall the policy when you finish your work. 

## SELinux_TE_Tester
The main tool for realizing the concept.
This tool make it possible to that!
1) This tool recives two parameters: a target domain and a verification program.
1) A policy is built for the program to executed as the domain.
1) The verification program is executed as the domain and the verification is done!!
1) The policy is removed...

### Reuirements
* python 2.x
* rpm-build
* policycoreutils-devel

### Usage
```
python selinux_te_tester.py <domain> <program>
```
* &lt;domain&gt;: a domain which you want to verify. (e.g. httpd_t)
* &lt;program&gt;: a verification program (e.g. script/access.py)

## script/access.py
A verification program. This verification will do below:
1) open, read and close to specified files
1) bind to specified ports

### How to specify files and ports
A config file is used to specify files and ports.
The file example is below:
```
dir, /var/www
file, /var/www/html/index.html
file, /etc/shadow
file, /etc/passwd
port, 1-10
port, 8080
```

"dir" is below:
* search files in a directory tree
* take care only files which be found, under permissions.
* ignore files which is not regular files or cannot get the attribute.

CAUTION: This script could hung up if some special file is read, i.e. trace_pipe. 


### Execution with selinux_te_tester
```
python selinux_te_tester.py <domain> script/access.py <config-file>
```

### Output Example
```
NG,open(r),file,/etc/shadow,[Errno 13] Permission denied: '/etc/shadow'
OK,open(r),file,/etc/passwd,-
OK,read,file,/etc/passwd,-
OK,close,file,/etc/passwd,-
NG,bind,port,1,[Errno 13] Permission denied
NG,bind,port,2,[Errno 13] Permission denied
NG,bind,port,3,[Errno 13] Permission denied
```

## Problem and Answer
This tool touches real resources. Thus, it is denger to verify writing or deleting files because the environment will be destroied!

However now, we have a good idea! A control of Type Enforcement goes along with SELinux domain and type. Therefore, writing to files as a type which is same with a file you want to verify, it could be said to done the verification for the files.

## SELinux_te_destroy_tester
This tool will do below:
1) Check SELinux types of target files.
1) Create dummy files which have same types with target files.
1) Write and delete to dummy files on a process as a target domain.

### Command
```
python selinux_te_destroy_tester.py <domain> <config-file>
```
* &lt;domain&gt;: a domain which you want to verify. (e.g. httpd_t)
* &lt;config-file&gt;: a config file written target files (e.g. conf/destory.conf.txt)

### Config File Example
```
/etc/shadow
/etc/passwd
```

### Output Example
```
NG,open(w),file,/etc/shadow,[Errno 13] Permission denied: '/root/workspace/te-tester/work/20180409120133882724_AjRkNZp8sO'
NG,delete,file,/etc/shadow,[Errno 13] Permission denied: '/root/workspace/te-tester/work/20180409120133882724_AjRkNZp8sO'
NG,open(w),file,/etc/passwd,[Errno 13] Permission denied: '/root/workspace/te-tester/work/20180409120133885883_dZP5omMCRC'
NG,delete,file,/etc/passwd,[Errno 13] Permission denied: '/root/workspace/te-tester/work/20180409120133885883_dZP5omMCRC'
```

## Contributing
We are grateful for contributing bug reports, bugfixes and improvements.
### Bug Report
Please open a new issue.

### Bugfixes and Improvements
Please open a new pull request.

## License
Copyright (C) 2018  Hitachi, Ltd.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

