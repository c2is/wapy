#WAPY AND WAPYD
This is a part of the Wapistrano [wapistrano](https://github.com/c2is/) project. 

##INSTALL
##Prerequisite
Please refer to Wapistrano readme, section about Capistrano server side.

###Add a specific user and install packages in /usr/local:

```shell
useradd wapyd -M -g adm
mkdir /var/log/wapyd/
chgrp adm /var/log/wapyd/
chmod 775 /var/log/wapyd/
cd /usr/local/
git clone git@gitlab.c2is.fr:a.cianfarani/wapy.git
cd wapy
./wapyd start
```

###CHECK CONFIGURATIONS
Open wapyd.cfg and control/adapt values (projects' path, gearman port...)

###START WAPYD
```
./wapyd start
```

###DISPLAY STATUS INFORMATIONS
```
./wapyd status
```

