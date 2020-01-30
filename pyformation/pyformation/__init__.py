import json
from pyformation.resources import Resource, Output, Transform, Parameters
from git import Repo
from pyformation import settings
import os

class Template():
    def __init__(self, root=True, project_name='', stack_name="stack"):
        self.items ={}
        self.properies = []
        self.root = root
        self.project_name = project_name
        self.stack_name = stack_name
        self.json = self.json_template()


    def add(self, obj):
        objecttype = self.__get_objecttype(obj)
        if objecttype in self.items:
            self.items[objecttype].append(obj)
        else:
            self.items[objecttype] = []
            self.items[objecttype].append(obj)

    def property(self, obj):
        self.properies.append(obj)

    def build(self):
        for item in self.properies:
            key, data = item.build_json()
            self.json[key]=data
        for objecttype, objects in self.items.items():
            self.json[objecttype] ={}
            for item in objects:
                key, data = item.build_json()
                self.json[objecttype][key] = data
        return json.dumps(self.json, sort_keys=True, indent=4)

    def json_template(self):
        template = {"AWSTemplateFormatVersion": "2010-09-09"}
        if self.project_name:
            repo = Repo(os.path.join(settings.PROJECT_DIR, self.project_name))
            commit_id = repo.head.commit.hexsha
            template['Description'] = '{}-{}'.format(self.stack_name, commit_id)
            params ={"Metadata": {"Comment": "Resource to update stack even if there are no changes",
                                  "GitCommitHash": commit_id}}
            self.add(Resource("CloudFormationDummyResource",
                              type="AWS::CloudFormation::WaitConditionHandle",
                              params=params))
        return template


    def __get_objecttype(self, obj):
        objecttype = None
        if isinstance(obj, Resource):
            objecttype = 'Resources'
        elif isinstance(obj, Output):
            objecttype = 'Outputs'
        elif isinstance(obj, Transform):
            objecttype = "Transform"
        elif isinstance(obj, Parameters):
            objecttype = "Parameters"
        return objecttype