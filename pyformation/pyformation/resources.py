from abc import ABC, abstractmethod
import hashlib
import json
import os
from pyformation import settings
from pyformation.utils.hash_url import hash_url
from pyformation.helpers import caps

class BaseResource(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def build_json(self):
        pass


class Resource(BaseResource):
    def __init__(self, name, type=None, params=None):

        self.name = self.colons_check(name)
        if params:
            self.params = self.params_dict(params)
        else:
            self.params=params
        self.type = type
        self.json = {}

    def build_json(self):
        if self.params:
            data = self.params
        else:
            data ={}
        data['Type']=self.type
        return self.name, data

    def colons_check(self, data):
        if data:
            if data[0] == ':':
                return caps(data[1:])
            else:
                return data
        else:
            return data

    def params_dict(self, params):
        new_params = {}
        for key, value in params.items():
            if isinstance(value, list):
                new_params[key] = self.params_list(value)
            elif isinstance(value, dict):
                new_params[key] = self.params_dict(value)
            elif isinstance(value, str):
                new_params[key] = self.colons_check(value)
            else:
                new_params[key] = value

        return new_params

    def params_list(self,params):
        new_params = []
        for param in params:
            if isinstance(param, list):
                new_params.append(self.params_list(param))
            elif isinstance(param, dict):
                new_params.append(self.params_dict(param))
            elif isinstance(param, str):
                new_params.append(self.colons_check(param))
            else:
                new_params.append(param)
        return new_params


class s3(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::S3::Bucket", params=params)


class Vpc(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::EC2::VPC", params=params)


class InternetGateway(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::EC2::InternetGateway", params=params)


class Route(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::EC2::Route", params=params)


class RouteTable(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::EC2::RouteTable", params=params)


class VPCGatewayAttachment(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::EC2::VPCGatewayAttachment", params=params)


class Subnet(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::EC2::Subnet", params=params)


class SubnetRouteTableAssociation(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::EC2::SubnetRouteTableAssociation", params=params)


class EcsCluster(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::ECS::Cluster", params=params)

class Output(BaseResource):
    def __init__(self, name, params=None):
        super().__init__()
        self.name = name
        self.params = params
        self.json = {}

    def build_json(self):
        data = self.params
        return self.name, data


class ServerlessFunction(Resource):
    def __init__(self, name, params=None):
        super().__init__(name, type="AWS::Serverless::Function", params=params)


class Transform(BaseResource):

    def build_json(self):
        return 'Transform', "AWS::Serverless-2016-10-31"


class Parameters(BaseResource):
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def build_json(self):
        return self.name, self.values


class Stack(Resource):
    def __init__(self, name, project_name, params=None):
        super().__init__(name, type="AWS::CloudFormation::Stack", params=params)
        self.project_name = project_name

    def build_json(self):

        if self.params:
            data = self.params
            if not 'Properties' in data:
                data['Properties'] = {}
        else:
            data ={'Properties':{}}
        data['Properties']['TemplateURL'] = hash_url(self.project_name, self.name)

        data['Type']=self.type
        return self.name, data

