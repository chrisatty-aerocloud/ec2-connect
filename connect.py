import argparse
import boto3
import sys
import inquirer
import subprocess

parser = argparse.ArgumentParser(description='Create an SSH session or SSH tunnel to an EC2 instance')
parser.add_argument('--region', type=str, help='AWS region', default='eu-west-2')
parser.add_argument('--profile', type=str, help='AWS profile', default='Company')
parser.add_argument('--tunnel', help='Create SSH tunnel', action='store_true')
parser.add_argument('--localport', help='Local port for SSH tunnel', default=8888)
parser.add_argument('--port', help='EC2 Port for SSH tunnel', default=27017)
parser.add_argument('--list', help='List EC2s and exit', action='store_true')

args = parser.parse_args()
session = boto3.Session(profile_name=args.profile)
client = session.client('ec2', region_name=args.region)

response = client.describe_instances()
instances = []
for r in response['Reservations']:
    for i in r['Instances']:
        for tag in i['Tags']:
            if tag['Key'] == 'Name':
                if args.list:
                    print(tag['Value'] + ' (' + i['InstanceId'] + ')')
                else:
                    instances.append({
                        'name': tag['Value'],
                        'instanceId': i['InstanceId']
                    })
if args.list:
    sys.exit(0)

ec2_options = list(map(lambda x: x['name'], instances))

instance_prompt = [
    inquirer.List('instance',
        message="Select an instance",
        choices=ec2_options,
        ),
]
prompt_result = inquirer.prompt(instance_prompt)
if prompt_result is None:
    sys.exit(0)

selected_instance = prompt_result['instance']
instance_data = next(filter(lambda x: x['name'] == selected_instance, instances), None)
if args.tunnel:
    cmd_args = [
        "aws",
        "ssm",
        "start-session",
        "--target", instance_data['instanceId'],
        "--profile", args.profile,
        "--region", args.region,
        "--document-name", "AWS-StartPortForwardingSession",
        "--parameters", '{"portNumber":["'+str(args.port)+'"],"localPortNumber":["'+str(args.localport)+'"]}'
    ]
    try:
        subprocess.run(cmd_args)
    except KeyboardInterrupt:
        sys.exit(0)
else:
    cmd_args = [
        "aws",
        "ssm",
        "start-session",
        "--target", instance_data['instanceId'],
        "--profile", args.profile,
        "--region", args.region
    ]
    try:
        subprocess.run(cmd_args)
    except KeyboardInterrupt:
        sys.exit(0)