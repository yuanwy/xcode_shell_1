#!/bin/bash

#SFTP配置信息
#用户名
USER=pack
#密码
PASSWORD=861020
#待上传文件根目录
SRCDIR=/Users/admin/Documents
#FTP目录
DESDIR=IOS/EJP
#IP
IP=197.255.20.72
#端口
PORT=21

#获取文件
cd ${SRCDIR} ;
#目录下的所有文件
#FILES=`ls` 
#修改时间在执行时间五分钟之前的xml文件
#FILES=`find ${SRCDIR} -mmin -50 -name '*.xml'`
FILES=config1.txt

for FILE in ${FILES}
do
    echo ${FILE}
#发送文件 (关键部分）
#lftp -u ${USER},${PASSWORD} sftp://${IP}:${PORT} <<EOF
ftp ftp://${USER}:${PASSWORD}@${IP}:${PORT} <<EOF
cd ${DESDIR}/
lcd ${SRCDIR}
put ${FILE}
by
EOF
done
