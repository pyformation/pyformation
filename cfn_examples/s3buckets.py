from pyformation import Template
from pyformation.resources import s3, Output


def build():
    #Create base template
    template = Template()

    #adding a s3 bucket
    template.add(s3('MyBucketName'))

    template.add(s3('MyAmazingBucket',params={'properties':{'BucketName':'some-unique-bucket-name'}}))

    [template.add(s3('MyOuststandingBucket{}'.format(x))) for x in range(3)]

    template.add(Output('MyExampleBucketName',params={'values':{'ref':'MyExampleS3BucketName'}}))

    print(template.build())