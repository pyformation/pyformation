from pyformation import settings
import os
from pyformation.utils.get_aws_data import get_specifications
from pyformation.utils.deploy_utils import create_stack, update_stack, stack_exists
from pyformation.utils.hash_url import hash_file
from pyfiglet import Figlet
from pyformation.setup_questions import *
from PyInquirer import prompt
from pyformation.render import render_file
import sys
import importlib
from git import Repo
import datetime
from dotenv import load_dotenv
import boto3

from datetime import datetime


'''
Main Script
'''


def upload(argv):
    print('upload started')
    if len(argv) < 3:
        return
    load_vars(argv)
    bucket = os.getenv('ARTIFACT_BUCKET', 'no-bucket')
    project_name = argv[2]
    # get build_stack list
    try:
        im_lib = importlib.import_module('projects.{}.stacks'.format(project_name))
        build_order = getattr(im_lib, 'build_order')
    except Exception as e:
        raise Exception("Project stack module not found")

    aws_access = os.getenv('AWS_ACCESS_KEY_ID', None)
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY', None)
    client = boto3.client('s3', aws_access_key_id=aws_access, aws_secret_access_key=aws_secret)
    bucket_exists = False
    for item in client.list_buckets():
        if item == bucket:
            bucket_exists = True
    if not bucket_exists:
        client.create_bucket(Bucket=bucket)
    files = []
    for stack in build_order:
        try:
            f = open('{}{}/build/{}.json'.format(settings.PROJECT_DIR, project_name, stack), 'rb')
        except Exception as e:
            print(e)
            raise Exception('Json stack not found. Check that the Compile has completed ok. Stack: {}'.format(stack))
        try:
            object_name = hash_file(project_name, stack)
        except Exception as e:
            raise Exception('Hash file name create failed. Stack:{}'.format(stack))
        try:
            response = client.upload_fileobj(f, bucket, object_name)
            files.append(object_name)
        except Exception as e:
            raise Exception('Upload to S3 failed for stack:{}'.format(stack))
    my_bucket = client.list_objects(Bucket=bucket)['Contents']
    print('Upload Completed')
    return build_order[-1], files


def deploy(argv):
    compile(argv)
    stack, files = upload(argv)
    bucket = os.getenv('ARTIFACT_BUCKET', 'no-bucket')
    for file in files:
        if stack.lower() in file:
            template_url = 'https://%s.s3.amazonaws.com/%s' % (bucket, file)
    stack_name = os.environ['STACK_NAME']
    if stack_exists(stack_name):
        print('updating stack')
        res = update_stack(stack_name, template_url, argv[2])
    else:
        print('creating stack')
        res = create_stack(stack_name,template_url, argv[2])

def compile(argv):
    print('Compiled Started')
    if len(argv)  < 3:
        print('No Project name was specified')
        return
    else:
        project_name =argv[2]
        try:
            repo = Repo('{}{}'.format(settings.PROJECT_DIR, argv[2]))
        except Exception as e:
            print(e)
            print("Failed to load the Git Repo")
            return
        repo.git.add('--all')
        try:
            repo.git.commit('-m', 'Compile Commit {}'.format(datetime.datetime.now().isoformat()))
        except:
            pass
        im_lib = importlib.import_module('projects.{}.stacks'.format(project_name))
        build_order = getattr(im_lib,'build_order')
        for item in build_order:
            build_stack(project_name, item)
        print('****   Compile Completed OK  ****')

def load_vars(argv):
    try:
        if len(argv) > 3:
            compile_type = argv[3]
        else:
            compile_type = 'test'
        if 'prod' in compile_type.lower():
            load_dotenv('{}{}/.env.production'.format(settings.PROJECT_DIR, argv[2]))
        elif 'rspec' in compile_type.lower():
            load_dotenv('{}{}/.env.rspec'.format(settings.PROJECT_DIR, argv[2]))
        else:
            load_dotenv('{}{}/.env.test'.format(settings.PROJECT_DIR, argv[2]))
    except:
        pass
    try:
        load_dotenv('{}{}/.env'.format(settings.PROJECT_DIR, argv[2]))
    except:
        pass
    try:
        load_dotenv('{}{}/.env.private'.format(settings.PROJECT_DIR, argv[2]))
    except:
        print('failed to load private')
        pass

def build_stack(project_name, stack_name):
    im_lib = importlib.import_module('projects.{}.stacks.{}'.format(project_name, stack_name))
    im_cls = getattr(im_lib, 'build')
    results = im_cls(project_name)
    with open('projects/{}/build/{}.json'.format(project_name, stack_name), 'w') as f:
        f.writelines(results)

def setup():
    if not os.path.exists(settings.DEFAULT_SPEC_LIB):
        os.makedirs(settings.DEFAULT_SPEC_LIB)
        open("{}__init__.py".format(settings.DEFAULT_SPEC_LIB), 'a').close()
        get_specifications()
    if not os.path.exists(settings.PROJECT_DIR):
        os.makedirs(settings.PROJECT_DIR)
        open("{}__init__.py".format(settings.PROJECT_DIR), 'a').close()

def newproject():
    f = Figlet(font='slant')
    print(f.renderText('PythonCFN'))
    answers = prompt(questions=questions)
    project_path = '{}{}/'.format(settings.PROJECT_DIR, answers['project_name'])
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        open("{}__init__.py".format(project_path), 'a').close()
        repo = Repo.init(project_path)
        for dir in settings.PROJECT_SUB_DIRS:
            os.makedirs("{}{}".format(project_path, dir))
            open("{}{}/__init__.py".format(project_path, dir), 'a').close()
        render_file('.env', answers, project_path)
        render_file('.env.production', answers, project_path)
        render_file('.env.test', answers, project_path)
        render_file('.env.rspec', answers, project_path)
        render_file('.gitignore', answers, project_path)
        render_file('ecsstack.py', answers, '{}stacks/'.format(project_path))
        render_file('parentstack.py', answers, '{}stacks/'.format(project_path))
        render_file('vpcstack.py', answers, '{}stacks/'.format(project_path))
        render_file('__init__.py', answers, '{}stacks/'.format(project_path))
        repo.git.add('--all')
        repo.git.commit('-m', 'inital Commit')

def run_build(argv):
    lib = argv[2]
    im_lib = None
    im_cls = None
    try:
        im_lib = importlib.import_module(lib)
    except Exception as e:
        print('failed to load module {}'.format(lib))
        print(e)
    try:
        if im_lib:
            im_cls = getattr(im_lib, 'build')
    except Exception as e:
        print('failed to load class : {} for  module :{}'.format(lib, 'build'))
        print(e)
    if im_cls:
        return im_cls()
    else:
        return None


def controller(argv=None):
    sys.path.append(os.getcwd())
    if not argv:
        argv = sys.argv
    try:
        command = argv[1].lower().strip()
    except:
        print('No command issued')
        raise Exception('No command Issued')
    if command == 'setup':
        setup()
    elif command == 'newproject':
        if not os.path.exists(settings.DEFAULT_SPEC_LIB):
            setup()
        newproject()
    elif command == 'build':
        load_vars(argv)
        try:
            file = argv[2]
        except:
            raise Exception('No file specified')
        print(run_build(argv))

    elif command == 'compile':
        load_vars(argv)
        compile(argv)

    elif command == 'upload':
        load_vars(argv)
        upload(argv)

    elif command =='deploy':
        load_vars(argv)
        deploy(argv)


