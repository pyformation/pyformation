import regex
from PyInquirer import Validator, ValidationError
from pyformation.utils.get_aws_data import get_regions

aws_regions = get_regions()


class ValidateProjectName(Validator):

    def validate(self, document):
        ok = regex.match("^([a-z0-9]*)$", document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid project name',
                cursor_position=len(document.text))


class ValidateAccountId(Validator):

    def validate(self, document):
        ok = regex.match("^([a-z0-9]*)$", document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid Account Id',
                cursor_position=len(document.text))


questions = [
    {
        'type': 'input',
        'name': 'project_name',
        'message': 'What\'s your project\'s name',
        'validate': ValidateProjectName
    },
    {
        'type': 'input',
        'name': 'aws_account_id',
        'message': 'What\'s your AWS Account ID',
        'validate': ValidateAccountId
    },
    {
        'type': 'list',
        'name': 'aws_region',
        'message': 'Select an AWS Region?',
        'choices': aws_regions
    }
]