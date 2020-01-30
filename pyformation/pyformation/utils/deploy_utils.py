import boto3
import os
from time import sleep


def get_client():
    aws_access = os.getenv('AWS_ACCESS_KEY_ID', None)
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY', None)
    aws_region = os.getenv('AWS_REGION', None)
    return boto3.client('cloudformation',region_name=aws_region, aws_access_key_id=aws_access, aws_secret_access_key=aws_secret )


def create_stack(stack_name, template_url, project_name):
    client = get_client()
    response = client.create_stack(
        StackName=stack_name,
        TemplateURL= template_url,
        TimeoutInMinutes=60,
        Capabilities=['CAPABILITY_IAM' , 'CAPABILITY_NAMED_IAM' , 'CAPABILITY_AUTO_EXPAND'],
        OnFailure='ROLLBACK' ,
        Tags=[
            {
                'Key': 'team',
                'Value': '{}'.format(project_name)
            },
        ],
    )


def update_stack(stack_name, template_url, project_name):
    client = get_client()
    response = client.update_stack(
        StackName=stack_name,
        TemplateURL=template_url,
        Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND'],
        Tags=[
            {
                'Key': 'team',
                'Value': '{}'.format(project_name)
            },
        ],
    )


def stack_exists(stack_name):
    client = get_client()
    stacks = client.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        elif stack['StackStatus'] == 'ROLLBACK_COMPLETE':
            response = client.delete_stack(StackName=stack_name)
            sleep(5)
            return stack_exists(stack_name)
        if stack_name == stack['StackName']:
            return True
    return False