from pyformation import Template
from pyformation.resources import Transform, Stack
from pyformation.helpers import *

def build(project_name):
    template = Template(project_name=project_name, stack_name='ParentStack')
    template.property(Transform())
    params={'Properties':{}, 'DependsOn': ['VpcStack']}
    params['Properties']["Parameters"] = {"Vpc": {"Fn::GetAtt": ["VpcStack", "Outputs.{{vars.project_name}}Vpc"]}}
    template.add(Stack('EcsStack', project_name, params=params))
    template.add(Stack('VpcStack', project_name, params={'Properties':{'TimeoutInMinutes':5}}))


    return template.build()