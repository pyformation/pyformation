from pyformation import Template
from pyformation.resources import Vpc, InternetGateway, Route, RouteTable, Output
from pyformation.resources import VPCGatewayAttachment, Subnet, SubnetRouteTableAssociation
import os
import math


def build():
    # same as
    #variable :cidr_block,
	#default: "10.0.0.0/16",
	#value: ENV["VPC_CIDR_BLOCK"

    cidr_block = os.getenv("VPC_CIDR_BLOCK", "10.0.0.0/16")

    #Creating base template
    template = Template()

    params = {'Properties':{}}
    params['Properties']['CidrBlock'] = cidr_block
    params['Properties']['Runtime'] = "nodejs10.x"
    params['Properties']['EnableDnsSupport'] = True
    params['Properties']['EnableDnsHostnames'] = True

    template.add(Vpc("ExampleVpc", params=params))

    template.add(InternetGateway('ExampleInternetGateway'))

    params = {'Properties': {}}
    params['Properties']['DestinationCidrBlock'] = "0.0.0.0/0"
    params['Properties']['GatewayId'] = {'Ref': "ExampleInternetGateway"}
    params['Properties']['RouteTableId'] = {'Ref': "ExampleRouteTable"}
    template.add(Route("ExampleRoute", params=params))

    params = {'Properties':{'VpcId':{'Ref':"ExampleVpc"}}}
    params['Properties']['Tags'] = [{'Key': "Environment", "Value": "Example Route Table"}]
    template.add(RouteTable("ExampleRouteTable", params=params))

    params = {'Properties':{}}
    params['Properties']['InternetGatewayId'] = {'Ref': "ExampleInternetGateway"}
    params['Properties']['VpcId'] = {"Ref": "ExampleVpc"}
    template.add(VPCGatewayAttachment("ExampleVpcGatewayAttachment", params=params))

    vpc_subnets = [
        {"name": "EsPrivate", "owner": "Example", "public": False, "offset": 1},
        {"name": "Ec2Public", "owner": "Example", "public": True,  "offset": 2},
        {"name": "Ec2Private", "owner": "Example", "public": False, "offset": 3},
        {"name": "BastionPublic", "owner": "Example", "public": True, "offset": 4 }
    ]

    for subnet in vpc_subnets:
        for x in range(0,3):
            params = {"Properties":{}}
            params['Properties']['AvailabilityZone'] = {"Fn::Select":[x , {"FnGetAZs": ""}]}
            params['Properties']["CidrBlock"] = {"FN::Select":[x +(3 * subnet['offset'])-3,
                                                               {"Fn::GetAtt": ["ExampleVpc", "CidrBlock"]},
                                                               str(3 * subnet['offset']),
                                                               str(math.floor(math.log(256) / math.log(2)))]}
            params['Properties']['MapPublicIpOnLaunch'] = subnet['public']
            params['Properties']['Tags'] = [{'Key': "owner", "Value": subnet['owner']}]
            params['Properties']['Tags'] = [{'Key': "resource_type", "Value": subnet['name']}]
            params['Properties']['VpcId'] = {"Ref": "ExampleVpc"}

            template.add(Subnet("Example{}SubNet".format(subnet["name"]), params=params))

        for x in range(0,3):
            params = {'Properties': {}}
            params['Properties']['RouteTableId'] = {'Ref': "ExampleRouteTable"}
            params['Properties']['SubnetId'] = "Example{}Subnet{}".format(subnet['name'], x)
            template.add(SubnetRouteTableAssociation("Example{}RouteTableAssociation".format(subnet['name']),
                                                     params=params))

        for x in range(0,3):
            template.add(Output('MyExampleBucketName', params={'values': {'ref': 'Example{}Subnet{}'.format(subnet['name'], x)}}))

    print(template.build())