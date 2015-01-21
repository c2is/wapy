#WAPY AND WAPYD
This is a part of the  [Wapistrano](https://github.com/c2is/) project. 

##INSTALL
##Prerequisite
Please refer to Wapistrano readme, section about Capistrano server side.

###Add a specific user and install packages in /usr/local:

```shell
useradd wapyd -M -g adm -d /usr/local/wapy/
mkdir /var/log/wapyd/
chgrp adm /var/log/wapyd/
chmod 775 /var/log/wapyd/
cd /usr/local/
git clone git@github.com:c2is/wapy.git
chown -R wapyd:adm /usr/local/wapy/
su wapyd
ssh-keygen
echo "Host *\n\tStrictHostKeyChecking no" > /usr/local/wapy/.ssh/config
exit
cd wapy
cp wapyd /etc/init.d/
update-rc.d wapyd defaults
```

###Add the rsa public key to your repositories:
```
cat /usr/local/wapy/.ssh/id_rsa.pub
```

###Create capistrano file storage area:

```shell
mkdir /var/capistrano
chgrp adm /var/capistrano
chmod 775 /var/capistrano
```

###CHECK CONFIGURATIONS
Open wapyd.cfg and control/adapt values (projects' path, gearman port...)

###START WAPYD
```
/etc/init.d/wapyd start
```

###DISPLAY STATUS INFORMATIONS
```
/etc/init.d/wapyd status
```

