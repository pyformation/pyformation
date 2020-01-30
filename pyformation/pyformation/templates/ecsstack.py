from pyformation import Template
from pyformation.resources import Transform, Parameters, Output, EcsCluster
from pyformation.helpers import *

def build(project_name):
    template = Template(project_name=project_name, stack_name='EcsStack')
    template.property(Transform())
    template.add(Parameters('Vpc', {'Description': "VPC ID", 'Type': 'String'}))
    template.add(EcsCluster('{{ vars.project_name }}EcsCluster'))

    template.add(Output('{{ vars.project_name }}EcsCluster', params={'Value': {'Ref':"{{ vars.project_name }}EcsCluster"}}))
    template.add(Output('{{ vars.project_name}}EcsClusterArn',
                        params={"Value": {"Fn::GetAtt": ["{{ vars.project_name}}EcsCluster", "Arn"]}}))

    return template.build()
