from pyformation import Template
from pyformation.resources import Transform, Parameters, Output, EcsCluster, Subnet
from pyformation.resources import InternetGateway, Vpc, Route, RouteTable, VPCGatewayAttachment
from pyformation.helpers import *
import math

def build(project_name):
    template = Template(project_name=project_name, stack_name='VpcStack')
    template.property(Transform())

    params = {'Properties':{}}
    params['Properties']['CidrBlock'] = "10.100.0.0/16"
    params['Properties']['EnableDnsSupport'] = True
    params['Properties']['EnableDnsHostnames'] = True

    template.add(Vpc("{{ vars.project_name }}Vpc", params=params))

    template.add(InternetGateway('{{ vars.project_name }}InternetGateway'))

    params = {'Properties': {}}
    params['Properties']['DestinationCidrBlock'] = "0.0.0.0/0"
    params['Properties']['GatewayId'] = {'Ref': "{{ vars.project_name }}InternetGateway"}
    params['Properties']['RouteTableId'] = {'Ref': "{{ vars.project_name }}RouteTable"}
    template.add(Route("{{ vars.project_name }}Route", params=params))

    params = {'Properties':{'VpcId':{'Ref':"{{ vars.project_name }}Vpc"}}}
    params['Properties']['Tags'] = [{'Key': "Environment", "Value": "{{ vars.project_name }} Route Table"}]
    template.add(RouteTable("{{ vars.project_name }}RouteTable", params=params))

    params = {'Properties':{}}
    params['Properties']['InternetGatewayId'] = {'Ref': "{{ vars.project_name }}InternetGateway"}
    params['Properties']['VpcId'] = {"Ref": "{{ vars.project_name }}Vpc"}
    template.add(VPCGatewayAttachment("{{ vars.project_name }}VpcGatewayAttachment", params=params))

    vpc_subnets = [
        {"name": "Ec2Public", "owner": "{{ vars.project_name }}", "public": True,  "offset": 2},
        {"name": "Ec2Private", "owner": "{{vars.project_name }}", "public": False, "offset": 3},
    ]


    for subnet in vpc_subnets:
        for x in range(0,3):
            params = {"Properties":{}}
            params['Properties']['AvailabilityZone'] = {"Fn::Select":[x , {"Fn::GetAZs": ""}]}
            params['Properties']["CidrBlock"] = {"Fn::Select":[x +(3 * subnet['offset'])-3,
                                                               {"Fn::Cidr": [
                                                                   {"Fn::GetAtt": ["{{ vars.project_name }}Vpc", "CidrBlock"]},
                                                                   str(3 * subnet['offset']),
                                                                   str(math.floor(math.log(256) / math.log(2)))
                                                               ]
                                                               }
                                                               ]
                                                 }
            params['Properties']['MapPublicIpOnLaunch'] = subnet['public']
            params['Properties']['Tags'] = [{'Key': "owner", "Value": subnet['owner']},
                                            {'Key': "resource_type", "Value": subnet['name']}]
            params['Properties']['VpcId'] = {"Ref": "{{ vars.project_name }}Vpc"}

            template.add(Subnet("{{ vars.project_name }}{}SubNet{}".format(subnet["name"], x), params=params))


    #template.add(Output('ExampleEcsCluster', params={'Value': {'Ref':"ExampleEcsCluster"}}))
    #template.add(Output('ExampleEcsClusterArn', params={"Value": {"Fn::GetAtt": ["ExampleEcsCluster", "Arn"]}}))
    for subnet in vpc_subnets:
        for x in range(0,3):
            template.add(Output("{{ vars.project_name }}{}SubNet{}Name".format(subnet["name"],x),
                                params={'Value': { 'Ref': '{{ vars.project_name}}{}SubNet{}'.format(subnet['name'], x)}}))
    template.add(Output("{{ vars.project_name}}Vpc", params={'Value': {'Ref':'{{ vars.project_name }}Vpc'}}))
    template.add(Output("VpcCidr", params={'Value':{ "Fn::GetAtt": ['{{ vars.project_name }}Vpc', 'CidrBlock']}}))
    return template.build()