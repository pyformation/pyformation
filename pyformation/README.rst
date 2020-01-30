***********
PyFormation
***********

Introduction
############
This module is designed to allow the user to build CloudFoundation JSON using Python
code instead of pure JSON. It is a port of RubyCFN as close as it can be

Installation and Setup
######################

Create a new Python environment

See link : https://docs.python.org/3/library/venv.html

PyFormation needs can easily be installed using PIP once done::

    pip install -e pyformation


QUICK START
###########

In the cfn_examples liobray are three examples of PyFormation. You can
build the JSON from these examples using the pyformation-admin command as below::

    pyformation-admin build cfn_examples.s3Buckets

This will print the results to the screen for you to review. Please
note that the Build command accepts an argument of python modules, not
a path to the file.

pyformation-admin command
#########################

This command is used for set-up, build directory structures for projects and
to directly build json from a given python script

pyformation-admin build *module*
********************************
This is the command that will build json directly from a python script
using the pythoncfn classes.
*module* should be written as though an import link to the file
i.e cfn_examples.deploy_serverless_function  , not as a path. See quickstart

pyformation-admin setup
***********************
This command downloads required information from AWS and stores it locally.
It will also set-up the base project file directory

pyformation-admin newproject
****************************
This takes you into a screen get the required info and build the project
framework needed. It will create the requried directrories in the /projects/ directory
and copy in the base files

pyformation-admin compile * *project* * *type*
**********************************************

This command compiles the files in a project into json that is then placed in the /build/
directory. The name of the project is required, but the TYPE is optional. It will default to Test.
This option states which of the .env.* files are loaded, and so which AWS credentials, buckets etc
are placed in the code. Options are test, production and rspec.

pyformation-admin upload * *project* *type*
*******************************************

This command will upload the created json files to the selected S3 bucket with the
correct hashed file names.

pyformation-admin deploy * *project* *type*
*******************************************

This command will compile, upload and deploy your CloundFormation files.


BUILDING YOU OWN STACKS
#######################

The Build or compile command will expect a number of things in a file to be true.

Firstly, it will expect to find a function called **build**, thus you MUST have a build
functions.

Secondly inside the build function it will expect to find the code to build the JSON needed
The main class for doing this is the **template** class. This class has the json build methods
plus the ability to accept any number of other objects to be bound to the template.

To add Resource or Output items, use the template.**add()** method, passing a requried
object of a Resource or output type.

To add a property key:value pair to the base template. use the template.**property()** method
with an appropriate Property object.

RESOURCE OBJECTS
****************

In pythoncfn, there is a base class called Resource::

    Resource('Resource_name', 'AWS::TYPE::OBJECT', params={'Some':'Dictionary of parameter objects})

You can use this base class to create any Resource type you like. However A set of child classes have been built
so that the Type parameter is done for you. This has been done so that in the future we can add validation on the
parameters passed to the given resource.

The following child classes are already created

#. s3
#. Vpc
#. InternetGateway
#. Route
#. RouteTable
#. VpcGatewayAttachment
#. Subnet
#. SubnetRouteTableAssociation
#. EcsCluster
#. ServerlessFunction
#. Stack

You can create your own classes and place them in the directory

    projects/**project_name**/custom/

PROJECT STACKS
**************

There are three stacks built for you when you create a project. Ecsstack, Vpcstack and parentstack. The ParentStack
contains details pointing to the other two stacks, thus its critical to the compile module that Ecsstack and Vpcstack
are built first.

Thus a build order for the compiler to follow is critical. This order can be found in

    /projects/**project_name**/stack.__init__.py



