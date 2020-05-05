from datetime import datetime
import click
import boto3
import yaml
import os
import json
import botocore

key_name = ""
s3_template_bucket_name = ""
db_username = ""
db_password = ""
environment = ""
stack_name = ""
version = ""
region = ""
cf = boto3.client('cloudformation', region_name='eu-west-1')


def parse_config(param_file):
    with open(param_file) as stream:
        global key_name, s3_template_bucket_name, db_username, db_password, environment, stack_name, version, region
        try:
            yaml_parsed = yaml.safe_load(stream)
            key_name = yaml_parsed.get('key_name')
            s3_template_bucket_name = yaml_parsed.get('s3_template_bucket_name')
            db_username = yaml_parsed.get('db_username')
            db_password = yaml_parsed.get('db_password')
            environment = yaml_parsed.get('environment')
            stack_name = yaml_parsed.get('stack_name')
            version = yaml_parsed.get('version')
            region = yaml_parsed.get('region')
        except yaml.YAMLError as exc:
            print(exc)


def update_templates():
    s3 = boto3.resource('s3', region_name='eu-west-1')
    directory = '../template/infra'
    try:
        for filename in os.listdir(directory):
            s3.meta.client.upload_file(directory + "/" + filename, s3_template_bucket_name, filename)
    except botocore.exceptions.ClientError as e:
        print("Unexpected error: %s" % e)


def _stack_exists(stack_name):
    stacks = cf.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def _parse_template(template):
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
  #  cf.validate_template(TemplateBody=template_data)
    return template_data

def cloud_formation_execute():

    try:
        #cf.validate_template(TemplateBody='template/master.yml')

        params = {
            'StackName': stack_name,
            'Parameters': [
                    {
                        'ParameterKey': 'NatKeyName',
                        'ParameterValue': key_name
                    },
                    {
                        'ParameterKey': 'BastionHostKeyName',
                        'ParameterValue': key_name
                    },
                    {
                        'ParameterKey': 'ApplicationHostKeyName',
                        'ParameterValue': key_name
                    },
                    {
                        'ParameterKey': 'EnvName',
                        'ParameterValue': environment
                    },
                    {
                        'ParameterKey': 'DBUsername',
                        'ParameterValue': db_username
                    },
                    {
                        'ParameterKey': 'DBPassword',
                        'ParameterValue': db_password
                    },
                    {
                        'ParameterKey': 'TemplateS3Bucket',
                        'ParameterValue': 'https://s3.amazonaws.com/' + s3_template_bucket_name
                    },
                    {
                        'ParameterKey': 'Version',
                        'ParameterValue': str(version)
                    }
            ],
            'TemplateBody': _parse_template('../template/master.yml'),
            'Capabilities': ['CAPABILITY_IAM'],
            'OnFailure': 'ROLLBACK'
        }
        if _stack_exists(stack_name):
            print('Updating {}'.format(stack_name))
            stack_result = cf.update_stack(**params)
            waiter = cf.get_waiter('stack_update_complete')
            waiter.wait(StackName=stack_name)
        else:
            print('Creating {}'.format(stack_name))
            stack_result = cf.create_stack(**params)
            waiter = cf.get_waiter('stack_create_complete')
            print("...waiting for stack to be ready...")
            waiter.wait(StackName=stack_name)
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("No changes")
        else:
            raise
    else:
        print(json.dumps(
            cf.describe_stacks(StackName=stack_result['StackId']),
            indent=2,
            default=json_serial
        ))


def _parse_parameters(parameters):
    with open(parameters) as parameter_fileobj:
        parameter_data = json.load(parameter_fileobj)
    return parameter_data


@click.command()
@click.option('--file', default='config.yaml')
def deploy(file):
    parse_config(file)
    update_templates()
    cloud_formation_execute()


if __name__ == '__main__':
    deploy()
