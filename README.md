# systems-puzzle

## Table of Contents
1. Description
1a. Note to GitHub users
2. Test environment
3. Usage
4. Thanks

## Description

This repository contains a solution to the Insight DevOps Engineering [challenge](https://github.com/InsightDataScience/systems-puzzle). See the link for a complete problem description.

## Note to GitHub users

The main repository is hosted on [BitBucket](https://bitbucket.org/lisaev1/insight-devops-systems-puzzle) (in Mercurial, and pushed to GitHub using the hggit extension). Please note that Git commit messages may contain references to non-existent commits because they are actually hg changeset id's. It is also possible that this mirror is outdated.

## Test environment

Docker is very invasive (and sucks in general), so to not ruin the host machine I used a clean Arch Linux virtual machine. Commands executed as root (regular user) are indicated by # ($). Yes, one can do things as a user in the "docker" group, but we are still pulling random images off the Internet, so meh... The relevant packages are:
```
$ pacman -Q | grep docker
docker 1:18.09.6-1
docker-compose 1.24.0-1
python-docker 4.0.1-1
python-docker-pycreds 0.4.0-1
python-dockerpty 0.4.1-4
```
I suggest installing the base image and then taking its rw snapshot, i.e. on the host:
```
$ # Make the image
$ qemu-img create -f qcow2 arch.qcow2 10G
$ 
$ # Install the system
$ qemu-system-x86_64 -enable-kvm -m 1G ... -drive file="arch.qcow2",if=virtio ...
$
$ # Take snapshot and boot it
$ qemu-img -f qcow2 -b ./arch.qcow2 arch-snapshot.qcow2
$ qemu-system-x86_64 -enable-kvm -m 1G ... -drive file="arch-snapshot.qcow2",if=virtio ...
```
Now if something goes wrong, kill the qemu process, rm the snapshot and start over.

## Usage

Clone the repo inside the VM and cd into the repo dir:
```
$ systemd-detect-virt
kvm
$ uname -a
Linux hyperarch 5.1.4-arch1-1-ARCH #1 SMP PREEMPT Wed May 22 08:06:56 UTC 2019 x86_64 GNU/Linux
$ echo -E "$PWD"
/home/lisaev/systems-puzzle
```

Next, follow instructions from assignment. First, we set up the database:
```
$ su -
Password:
# cd /home/lisaev/systems-puzzle
# docker-compose up -d db
...
# docker-compose run --rm flaskapp /bin/bash -c "cd /opt/services/flaskapp/src && python -c  'import database; database.init_db()'"
...
```
and verify that it's OK:
```
# docker ps --format '{{.ID}}' --filter "name=systems-puzzle_db_1"
6474674f3c70
# docker exec -it 6474674f3c70 /bin/bash
root@6474674f3c70:/# su -l postgres
No directory, logging in with HOME=/
$ psql
psql (9.6.5)
Type "help" for help.

postgres=# \l
                                  List of databases
    Name     |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges   
-------------+----------+----------+------------+------------+-----------------------
 flaskapp_db | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
 postgres    | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
 template0   | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
             |          |          |            |            | postgres=CTc/postgres
 template1   | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
             |          |          |            |            | postgres=CTc/postgres
(4 rows)

postgres=# \c flaskapp_db
You are now connected to database "flaskapp_db" as user "postgres".
flaskapp_db=# \dt
         List of relations
 Schema | Name  | Type  |   Owner   
--------+-------+-------+-----------
 public | items | table | docker_pg
(1 row)

flaskapp_db=# select * from items;
 id | name | quantity | description | date_added 
----+------+----------+-------------+------------
(0 rows)
```
Second, we bring up the rest of the application with
```
# docker-compose up -d
...
# docker ps
# docker ps --format "{{.ID}} {{.Names}} {{.Ports}}"
d6f462e55759 systems-puzzle_nginx_1 0.0.0.0:8080->80/tcp
7e71ab6679b4 systems-puzzle_flaskapp_1 5001/tcp
6474674f3c70 systems-puzzle_db_1 5432/tcp
```
This last docker-compose command is to be used every time we want to start the entire application (e.g. after rebooting the VM).

Assuming the application is up and running, there should be port-forwarding through NAT from port 8080 on the VM to port 80 in the nginx container. Therefore, one can connect to the VM from a browser on the host (using qemu bridge networking).

After entering few items:
```
flaskapp_db=# select * from items;
 id |                name                | quantity | description |         date_added         
----+------------------------------------+----------+-------------+----------------------------
  1 | Armani                             |        3 | shoes       | 2019-05-25 21:32:26.488658
  2 | Rolex                              |        1 | watch       | 2019-05-25 21:32:46.516191
  3 | Hitachi                            |        1 | TV          | 2019-05-25 21:36:00.664181
  4 | Dell Precision                     |        1 | tech        | 2019-05-25 21:38:47.240023
  5 | Apple MacBook Pro 15'' retine      |        1 | tech        | 2019-05-25 21:47:10.106953
  6 | gnfek                              |       44 | alanc       | 2019-05-25 22:40:07.068937
  7 | HP EliteBook                       |        2 | tech        | 2019-05-25 22:47:46.426146
  8 | A & B Strugatsky, Hard to be a God |        1 | books       | 2019-05-25 22:55:39.155133
(8 rows)
```

## Thanks

1. [PostgreSQL Exercises](https://pgexercises.com)
2. [Arch Linux](https://www.archlinux.org)
3. [PostgreSQL -- ArchWiki](https://wiki.archlinux.org/index.php/PostgreSQL)
