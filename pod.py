# -*- coding:utf-8 -*-
#!/usr/bin/python
#
import os
import sys
import json
import requests

JOB_NAME = os.getenv("JOB_BASE_NAME")
GIT_URL = 'http://git.yijiupidev.com:81'
REPO_URL = 'http://git.yijiupidev.com:81/iOSProjects/EJPSpecsManager.git,http://git.yijiupidev.com:81/CommentAssemblies/EJPCommentAssembliesSpecManager.git'
PER_PAGE = 50
CHARSET = 'export LANG=en_US.UTF-8 && export LANGUAGE=en_US.UTF-8 && export LC_ALL=en_US.UTF-8'

class GitLabAPI(object):
    def __init__(self, headers=None, *args, **kwargs):
        self.headers = headers

    def get_group_id(self,url):
        group_id = {}
        res = requests.get("%s/api/v3/groups" %url, headers=self.headers, verify=False)
        status_code = res.status_code
        content = res.json()
        for i in content:
            group_id[i['id']] = i['name']
        return group_id

    def get_group_project(self,url,group_id,page):
        os.system("export LANG=en_US.UTF-8 && export LANGUAGE=en_US.UTF-8 && export LC_ALL=en_US.UTF-8")
        for i in group_id:
            res = requests.get("%s/api/v3/groups/%s/projects?per_page=%s" %(url,group_id[i],page),headers=self.headers,verify=False)
            status_code = res.status_code
            content = res.json()
            for j in content:
				if JOB_NAME in j['name']:
                    #print(j['name'],group_id[i])
					os.system("%s && /usr/local/bin/pod repo update %s" %(CHARSET,group_id[i]))
					os.system("%s && /usr/local/bin/pod spec lint %s.podspec --sources=%s --verbose --allow-warnings --use-libraries" %(CHARSET,JOB_NAME,REPO_URL))
					os.system("%s && /usr/local/bin/pod repo push %s %s.podspec --verbose --allow-warnings  --use-libraries" %(CHARSET,group_id[i],JOB_NAME))

if __name__ == "__main__":
    headers = {'PRIVATE-TOKEN': 'zvWywUx5B-1PdMsz2dVq'} #你的gitlab账户的private token
    api = GitLabAPI(headers=headers)
    gid = api.get_group_id(GIT_URL)
    if gid:
        api.get_group_project(GIT_URL,gid,PER_PAGE)
