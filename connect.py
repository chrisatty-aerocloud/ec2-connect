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
parser.add_argument('--name', type=str, help='Name of EC2 instance to connect to')
parser.add_argument('--instanceId', type=str, help='Instance ID of EC2 instance to connect to')

args = parser.parse_args()
if args.name and args.instanceId:
    print("Please provide either a name or an instanceId, not both")
    sys.exit(1)

session = boto3.Session(profile_name=args.profile)
client = session.client('ec2', region_name=args.region)

response = client.describe_instances()
instances = []
for r in response['Reservations']:
    for i in r['Instances']:
        instance = {
            'instanceId': i['InstanceId'],
            'name': None
        }
        if 'Tags' in i:
            for tag in i['Tags']:
                if tag['Key'] == 'Name':
                    instance['name'] = tag['Value']
        instances.append(instance)

if args.list:
    for instance in instances:
        if instance['name'] is None:
            print(instance['instanceId'])
        else:
            print(instance['name'] + " (" + instance['instanceId'] + ")")
    sys.exit(0)

ec2_options = list(map(lambda x: x['name'] if x['name'] is not None else x['instanceId'], instances))
instanceId = None
if not args.name and not args.instanceId:
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
    instance_data = next(filter(lambda x: x['name'] == selected_instance or x['instanceId'] == selected_instance, instances), None)
    instanceId = instance_data['instanceId']
elif args.name:
    instance_data = next(filter(lambda x: x['name'] == args.name, instances), None)
    if instance_data is None:
        print("Instance with name " + args.name + " not found")
        sys.exit(1)
    instanceId = instance_data['instanceId']
elif args.instanceId:
    instance_data = next(filter(lambda x: x['instanceId'] == args.instanceId, instances), None)
    if instance_data is None:
        print("Instance with ID " + args.instanceId + " not found")
        sys.exit(1)
    instanceId = instance_data['instanceId']

if args.tunnel:
    print("Creating SSH tunnel to " + instanceId + " on port " + str(args.port) + " to local port " + str(args.localport))
    cmd_args = [
        "aws",
        "ssm",
        "start-session",
        "--target", instanceId,
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
    print("Creating SSH session to " + instanceId)
    cmd_args = [
        "aws",
        "ssm",
        "start-session",
        "--target", instanceId,
        "--profile", args.profile,
        "--region", args.region
    ]
    try:
        subprocess.run(cmd_args)
    except KeyboardInterrupt:
        sys.exit(0)