import boto3
import json
import datetime

ec2 = boto3.client('ec2')
logs = boto3.client('logs')

LOG_GROUP = "/incident-response/remediation-actions"
LOG_STREAM = "lambda-remediation"


def log_action(message):
    """Write remediation action to CloudWatch Logs."""
    timestamp = int(datetime.datetime.utcnow().timestamp() * 1000)
    try:
        logs.create_log_group(logGroupName=LOG_GROUP)
    except logs.exceptions.ResourceAlreadyExistsException:
        pass
    try:
        logs.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
    except logs.exceptions.ResourceAlreadyExistsException:
        pass

    logs.put_log_events(
        logGroupName=LOG_GROUP,
        logStreamName=LOG_STREAM,
        logEvents=[{'timestamp': timestamp, 'message': message}]
    )


def lambda_handler(event, context):
    """
    Triggered by CloudWatch Alarm (via SNS) when EC2 CPU > threshold.
    Restarts the offending instance as remediation action.
    """
    print("Event received:", json.dumps(event))

    # Extract instance ID from SNS message (CloudWatch alarm dimensions)
    message = json.loads(event['Records'][0]['Sns']['Message'])
    alarm_name = message.get('AlarmName', 'unknown')
    dimensions = message.get('Trigger', {}).get('Dimensions', [])
    instance_id = next((d['value'] for d in dimensions if d['name'] == 'InstanceId'), None)

    if not instance_id:
        log_action(f"ERROR: No InstanceId found in alarm '{alarm_name}' payload.")
        return {"statusCode": 400, "body": "No instance ID found"}

    try:
        ec2.reboot_instances(InstanceIds=[instance_id])
        log_action(f"REMEDIATION: Instance {instance_id} rebooted due to alarm '{alarm_name}' (high CPU).")
        return {"statusCode": 200, "body": f"Instance {instance_id} rebooted successfully"}
    except Exception as e:
        log_action(f"ERROR: Failed to remediate instance {instance_id}: {str(e)}")
        return {"statusCode": 500, "body": str(e)}
