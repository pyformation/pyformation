from pyformation import Template
from pyformation.resources import Transform, ServerlessFunction
import os




def build():
    lambda_bucket = os.getenv("LAMBDA_BUCKET", "my-serverless-bucket"
                               )
    #Create base template
    template = Template()

    #adding transform property to the base
    template.property(Transform())

    #bulding parameters for the serverless deploy
    params = {'Properties':{}}
    params['Properties']['Handler'] = "index.labda_handler"
    params['Properties']['Runtime'] = "nodejs10.x"
    params['Properties']['CodeUri'] = "s3//{}/labda_function.zip".format(lambda_bucket)
    params['Properties']['Description'] = "My Serverless Labda Function"
    params['Properties']['Timeout'] = 30
    params['Properties']['Events'] = {}
    params['Properties']['Events']['Compiler'] ={}
    params['Properties']['Events']['Compiler']['Type'] = "Api"
    params['Properties']['Events']['Compiler']['Properties'] = {'path': "/", "method": "post"}

    template.add(ServerlessFunction("MyServerlessFunction", params=params))

    print(template.build())