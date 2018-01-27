#!/bin/bash
#

export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

JOB_NAME=${JOB_NAME##*/}

/usr/local/bin/pod spec lint $JOB_NAME.podspec --sources='http://git.yijiupidev.com:81/iOSProjects/EJPSpecsManager.git,http://git.yijiupidev.com:81/CommentAssemblies/EJPCommentAssembliesSpecManager.git' --verbose --allow-warnings --use-libraries

/usr/local/bin/pod repo push EJPSpecsManager $JOB_NAME.podspec --verbose --allow-warnings  --use-libraries 
