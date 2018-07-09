# SELinux Type Enforcement Tester

## コンセプト
SELinuxのポリシー設定の確認は、対象のプロセスが設計したセキュリティポリシーに従って、正しくアクセス許可/アクセス拒否されるかどうかを確認しなければいけません。この確認は、不正アクセスを想定するため、通常ならアクセスしないファイルやポートに対してアクセス操作を行う必要があります。これらの確認は、対象のプロセスが通常行う動作でないことを実施する必要があるため、確認を行うこと自体が非常に困難です。  
このSELinux Type Enforcement Tester は、この検証作業を簡易化するためのツールです。
このプログラムは、専用の検証用プログラムを、検証を行いたいプロセスと同じドメインで動作させることで、Type Enforcement(TE)の検証を行います。


## 前提条件
* SELinuxモジュールをインストールできるユーザで実行してください。そうでないと実行エラーになります。
* SELinuxのモードがEnforcingでないと検証できません。Permissive,disabledでは正しい結果を得ることが出来ません。

## 実行環境
* python 2.x
* rpm-build
* policycoreutils-devel

## 注意事項
* 検証プログラムの実行前後で、ポリシーのインストールに３０秒、アンインストールに１０秒程度の時間を要します。
* 実行結果をファイルに保存する必要がある場合、リダイレクトを使用してください。
* 実行後、ポリシーが削除されるため、audit2allowなどは正常に機能しません。
* ポリシーをアンインストールしたくない場合、コマンドライン引数の先頭に--disabled-uninstall-policyを設定してください。必 要なくなったらポリシーは必ずアンインストールしてください。

## ツールの構成
本ツールは、SELinux_TE_Tester本体と検証用プログラムの2つのプログラムで構成されます。
以下のようにコマンドラインで実行します。
```
python selinux_te_tester.py <domain> 検証用プログラム <config-file>
```
* selinux_te_tester.py：ツールの本体です。
* domain：検証を行いたいSELinux上のドメインを指定します。
* 検証用プログラム：ファイルやポートなどへのアクセス方法を記載したプログラムです。
* config-file：検証プログラムの設定ファイルです。検証を行いたいファイルやポートを指定します。

### selinux_te_tester.py
SELinux_TE_Testerのコンセプトを実現するメインツールです。以下のように動作します。
1) 対象となるドメインと検証プログラムのパスを受け取ります。
1) 検証プログラムを対象ドメインで動作されるSELinuxポリシーを構築・インストールします。
1) 検証プログラムを実行します。
1) ポリシーをアンインストールします。

### domain
検証を行いたいドメインを指定します。

### 検証用プログラム
検証用プログラムによって、対象のファイルやプロセスへのアクセスを行います。
このプログラムは、ユーザが自由に作成することができます。
サンプルとして基本的なアクセスを行う検証用プログラムを用意しています。
ファイルとポート以外の確認を行いたい場合は、自ら検証用プログラムを作成してください。そして公開してください。

## 検証用プログラムのサンプル
### script/access.py
検証プログラムのサンプルです. 以下を検証します。
1) 指定のファイルに対して、open、read、closeを実行します。
1) 指定のポートに対してbindを試みます。

### config-file
検証プログラムに読み込ませて検証を行うファイルやポートを指定するファイルです。
### ファイルとポートの指定方法
コンフィグファイルに以下のように指定してください。
```
dir, /var/www
file, /var/www/html/index.html
file, /etc/shadow
file, /etc/passwd
port, 1-10
port, 8080
```

"dir" について:
* ディレクトリツリーを検索します。
* パーミッション下で見つかったファイルのみ対象とします
* 通常ファイル以外または属性が取得できないファイルも無視します

CAUTION: このスクリプトに読み込ませるとハングアップする特殊なファイルがあります。i.e. trace_pipe.



実行例：
本ツール付属のサンプルを用いた実行例
te-testerディレクトリで実行

### selinux_te_testerを用いた実行
```
python selinux_te_tester.py http_d script/access.py config/conf.csv
```

### 出力例
```
NG,open(r),file,/etc/shadow,[Errno 13] Permission denied: '/etc/shadow'
OK,open(r),file,/etc/passwd,-
OK,read,file,/etc/passwd,-
OK,close,file,/etc/passwd,-
NG,bind,port,1,[Errno 13] Permission denied
NG,bind,port,2,[Errno 13] Permission denied
NG,bind,port,3,[Errno 13] Permission denied
（略）
OK,bind,port,8080,-
```

## 書き込み権限と削除権限の検証について
書込み・削除の検証は環境を破壊する危険があります。
しかし、TEによる制御はSELinuxのタイプとドメインに沿ったものなので、検証したいファイルと同じタイプのファイルを用意し、そのファイルに書込みを行えば、対象のファイルに対するTEを検証できます。  
この書き込みと削除を確認するツールは、検証用プログラムではなくてSELinux_TE_Testerの一つのバリエーションモデルとなります。

## 書き込みと削除を検証するツール
### SELinux_te_destroy_tester
このツールは以下のように動作します。
1) 検証対象となるファイルのSELinuxタイプを調べます。
1) 検証ファイルと同じタイプをもつダミーファイルを作成します。
1) 検証対象のドメインを持つプロセスから書込み・削除をダミーファイルに対して実行します。

### コマンド
SELinux_TE_Testerとコマンドラインの構成が異なるので注意してください。
```
python selinux_te_destroy_tester.py <domain> <config-file>
```
* &lt;domain&gt;: 検証対象のドメイン (e.g. httpd_t)
* &lt;config-file&gt;: 検証対象のファイルを指定したコンフィグファイルのパス (e.g. conf/destory.conf.txt)

### コンフィグファイルの例
```
/etc/shadow
/etc/passwd
```

### 出力例
```
NG,open(w),file,/etc/shadow,[Errno 13] Permission denied: '/root/workspace/te-tester/work/20180409120133882724_AjRkNZp8sO'
NG,delete,file,/etc/shadow,[Errno 13] Permission denied: '/root/workspace/te-tester/work/20180409120133882724_AjRkNZp8sO'
NG,open(w),file,/etc/passwd,[Errno 13] Permission denied: '/root/workspace/te-tester/work/20180409120133885883_dZP5omMCRC'
NG,delete,file,/etc/passwd,[Errno 13] Permission denied: '/root/workspace/te-tester/work/20180409120133885883_dZP5omMCRC'
```

## 貢献
バグ報告・修正・改良は歓迎します。
### バグ報告
Issueを作成ください。

### 修正・改良
プルリクエストを送ってください。

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
along with this program.  If not, see &lt;https://www.gnu.org/licenses/&gt;.
