#WAPY AND WAPYD
This is a part of the Wapistrano project

##INSTALL
Add a specific user and install packages in /usr/local:

```
useradd wapyd -M -g adm
mkdir /var/log/wapyd/
chgrp adm /var/log/wapyd/
cd /usr/local/
git clone git@gitlab.c2is.fr:a.cianfarani/wapy.git
cd wapy
./wapyd start
```

To see some process information run:

```
./wapyd status
```

