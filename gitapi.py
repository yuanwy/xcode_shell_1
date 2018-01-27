# -*- coding:utf-8 -*-

import requests
from common.utils import ServerError


class GitLabAPI(object):
    def __init__(self, headers=None, *args, **kwargs):
        self.headers = headers

    def get_user_id(self, username):
        user_id = None
        res = requests.get("http://git.yijiupidev.com:81/api/v3/users?username=%s"%username, headers=self.headers, verify=False)
        status_code = res.status_code
        if status_code != 200:
            raise ServerError(res.get('message'))
        content = res.json()
        if content:
            user_id = content[0].get('id')
        return user_id

    def get_user_projects(self):
        res = requests.get("http://git.yijiupidev.com:81/api/v3/projects", headers=self.headers, verify=False)
        status_code = res.status_code
        if status_code != 200:
            raise ServerError(res.get('message'))
        content = res.json()
        return content

    def get_user_project_id(self, name):
        """
        :param name: 项目名称 
        :return: 
        """
        project_id = None
        projects = self.get_user_projects()
        if projects:
            for item in projects:
                if item.get('name') == name:
                    project_id = item.get('id')
        return project_id

    def get_project_branchs(self, project_id):
        branchs = []
        res = requests.get("http://git.yijiupidev.com:81/api/v3/projects/%s/repository/branches"%project_id, headers=self.headers, verify=False)
        status_code = res.status_code
        if status_code != 200:
            raise ServerError(res.get('message'))
        content = res.json()
        if content:
            for item in content:
                branchs.append(item.get('name'))
        return branchs

    def get_project_tags(self, project_id):
        tags = []
        res = requests.get("http://git.yijiupidev.com:81/api/v3/projects/%s/repository/tags" % project_id,
                           headers=self.headers, verify=False)
        status_code = res.status_code
        if status_code != 200:
            raise ServerError(res.get('message'))
        content = res.json()
        if content:
            for item in content:
                tag_name = item.get('name')
                commit = item.get('commit')
                info = ''
                if commit:
                    commit_id = commit.get('id')
                    commit_info = commit.get('message')
                    info = "%s * %s"%(commit_id[:9], commit_info)
                tags.append("%s     %s"%(tag_name, info))
        return tags


if __name__ == "__main__":
    headers = {'PRIVATE-TOKEN': 'zvWywUx5B-1PdMsz2dVq'} #你的gitlab账户的private token
    api = GitLabAPI(headers=headers)
    content = api.get_user_projects()

    user_id = api.get_user_id('duyong')
    print "user_id:", user_id

    #project_id = api.get_user_project_id('project1')
    #print "project:", project_id

    #branchs = api.get_project_branchs('345')
    #print "project branchs:", branchs

    #tags = api.get_project_tags('345')
    #print "project tags:", tags


