# Automated Incident Response System using CloudWatch Alarms & Lambda Remediation

## Project Overview

This project demonstrates an automated incident response solution on AWS using Amazon CloudWatch, Amazon SNS, AWS Lambda, and CloudWatch Logs. The solution continuously monitors the CPU utilization of an Amazon EC2 instance and automatically remediates high CPU incidents without manual intervention.

When CPU utilization exceeds the configured threshold for a sustained period, a CloudWatch Alarm changes to the **ALARM** state and publishes a notification to an Amazon SNS topic. The SNS topic invokes an AWS Lambda function that automatically reboots the affected EC2 instance and records the remediation action in CloudWatch Logs for auditing and troubleshooting.

This event-driven architecture minimizes downtime, improves operational reliability, and provides a complete audit trail for every automated remediation event.

---

# Architecture

```text
                    Automated Incident Response

      +-----------------------+
      |   Amazon EC2 Instance |
      |    web-server-prod    |
      +-----------+-----------+
                  |
          CPU Utilization > 80%
                  |
                  ▼
      +-----------------------+
      | CloudWatch Alarm      |
      |   HighCPUAlarm        |
      +-----------+-----------+
                  |
                  ▼
      +-----------------------+
      | Amazon SNS Topic      |
      | cpu-alarm-topic       |
      +-----------+-----------+
                  |
                  ▼
      +-----------------------+
      | AWS Lambda            |
      | remediation_function  |
      +-----------+-----------+
                  |
        +---------+---------+
        |                   |
        ▼                   ▼
 Reboot EC2 Instance   CloudWatch Logs
```

---

# Folder Structure

```text
project4/
├── README.md
├── cloudwatch/
│   ├── create-cpu-alarm.sh
│   └── generate-load.sh
├── lambda/
│   ├── remediation_function.py
│   └── lambda-execution-role-policy.json
└── screenshots/
    ├── 01-cloudwatch-alarm-configured.png
    ├── 02-sns-lambda-subscription.png
    ├── 03-cpu-utilization-graph.png
    ├── 04-alarm-state-alarm.png
    ├── 05-lambda-execution.png
    ├── 06-cloudwatch-remediation-logs.png
    └── SCREENSHOTS.md
```

---

# Scenario

Production workloads occasionally experienced sustained CPU spikes that degraded application performance. Previously, administrators had to manually detect the issue, investigate the instance, reboot the server, and verify service recovery.

This project automates the complete incident response lifecycle by:

- Continuously monitoring EC2 CPU utilization
- Detecting sustained threshold breaches
- Publishing notifications using Amazon SNS
- Automatically invoking an AWS Lambda remediation function
- Rebooting the affected EC2 instance
- Logging every remediation event to CloudWatch Logs

This implementation demonstrates a practical self-healing infrastructure pattern using native AWS services.

---

# AWS Environment

| Property | Value |
|----------|-------|
| AWS Account ID | **259151461533** |
| AWS Account Alias | **atharv** |
| AWS Region | **us-east-1** |
| EC2 Instance | **web-server-prod** |
| EC2 Instance ID | **i-0d8a7b4c9f1234567** |
| CloudWatch Alarm | **HighCPUAlarm** |
| SNS Topic | **cpu-alarm-topic** |
| Lambda Function | **remediation_function** |
| IAM Role | **LambdaRemediationRole** |
| CloudWatch Log Group | **/incident-response/remediation-actions** |
| Runtime | **Python 3.12** |

---

# Step 1 — Configure CloudWatch Monitoring

Create an Amazon SNS topic.

```bash
aws sns create-topic --name cpu-alarm-topic
```

Run the alarm creation script.

```bash
./cloudwatch/create-cpu-alarm.sh
```

The alarm monitors Amazon EC2 CPU utilization and publishes notifications whenever CPU usage remains above the configured threshold.

### Alarm Configuration

| Setting | Value |
|---------|-------|
| Metric | CPUUtilization |
| Namespace | AWS/EC2 |
| Statistic | Average |
| Threshold | Greater than 80% |
| Evaluation Periods | 2 |
| Datapoints to Alarm | 2 of 2 |
| Period | 5 Minutes |
| Alarm Action | Publish to SNS Topic |

---

## Screenshot 1 — CloudWatch Alarm Configured

This screenshot displays the CloudWatch Alarm configuration.

It verifies:

- Alarm Name: **HighCPUAlarm**
- Metric: **CPUUtilization**
- Threshold: **80%**
- Evaluation Periods: **2**
- Alarm State: **OK**
- SNS Action: **cpu-alarm-topic**

![](./screenshots/01-cloudwatch-alarm-configured.png)

---

# Step 2 — Configure AWS Lambda Remediation

Create the Lambda execution role using the IAM policy included in this project.

Deploy the Lambda function using Python 3.12 runtime.

Subscribe the Lambda function to the SNS topic.

```bash
aws sns subscribe \
--topic-arn arn:aws:sns:us-east-1:259151461533:cpu-alarm-topic \
--protocol lambda \
--notification-endpoint <LAMBDA_ARN>
```

Grant Amazon SNS permission to invoke Lambda.

```bash
aws lambda add-permission \
--function-name remediation_function \
--statement-id sns-invoke \
--action lambda:InvokeFunction \
--principal sns.amazonaws.com
```

The Lambda function performs the following actions automatically:

- Receives the SNS notification
- Parses the CloudWatch alarm payload
- Identifies the affected EC2 instance
- Calls the EC2 RebootInstances API
- Writes remediation details to CloudWatch Logs

---

## Screenshot 2 — SNS to Lambda Subscription

This screenshot confirms that the Amazon SNS topic has an active Lambda subscription.

Subscription Details:

- Topic: **cpu-alarm-topic**
- Protocol: **Lambda**
- Endpoint: **remediation_function**
- Status: **Confirmed**

![](./screenshots/02-sns-lambda-subscription.png)

---

# Step 3 — Generate High CPU Load

Run the stress test script.

```bash
./cloudwatch/generate-load.sh
```

The script increases CPU utilization until it exceeds the configured alarm threshold.

CloudWatch continuously evaluates the metric and changes the alarm state to **ALARM** after two consecutive evaluation periods.

The alarm notification is automatically delivered to Amazon SNS, which invokes the remediation Lambda function.

---

## Screenshot 3 — CloudWatch Metrics

The CloudWatch Metrics graph shows CPU utilization gradually increasing beyond the configured 80% threshold.

This validates that the monitoring configuration successfully detects sustained high CPU utilization.

![](./screenshots/03-cpu-utilization-graph.png)

---

## Screenshot 4 — Alarm State Changed to ALARM

This screenshot shows the CloudWatch Alarm after the configured threshold has been exceeded.

The alarm transitions from **OK** to **ALARM**, confirming successful monitoring and event detection.

The alarm history also records the exact time the state changed.

![](./screenshots/04-alarm-state-alarm.png)

---

# Step 4 — Automated Incident Remediation

Once the alarm enters the **ALARM** state, the remediation workflow is triggered automatically.

Workflow:

1. CloudWatch Alarm enters ALARM state.
2. Amazon SNS publishes the notification.
3. AWS Lambda receives the event.
4. Lambda reboots the EC2 instance.
5. Lambda records the remediation activity in CloudWatch Logs.

## Screenshot 5 — Lambda Function Execution

This screenshot shows the successful execution of the AWS Lambda remediation function after receiving the CloudWatch Alarm notification through Amazon SNS.

The Lambda monitor page displays:

- Function Name: **remediation_function**
- Runtime: **Python 3.12**
- Invocation Status: **Success**
- Recent Invocation
- Execution Duration
- Memory Utilization
- CloudWatch Logs Link

![](./screenshots/05-lambda-execution.png)

---

# Step 5 — CloudWatch Logging

Every automated remediation performed by AWS Lambda is recorded in Amazon CloudWatch Logs.

Each log entry contains:

- Timestamp
- Alarm Name
- EC2 Instance ID
- Action Performed
- Execution Status
- Request ID

Maintaining these logs provides complete operational visibility and creates an audit trail for every automated incident response.

---

## Screenshot 6 — CloudWatch Remediation Logs

This screenshot displays the CloudWatch Log Group containing the remediation history generated by the Lambda function.

The log entries include:

- Alarm Name: **HighCPUAlarm**
- EC2 Instance: **web-server-prod**
- Instance ID: **i-0d8a7b4c9f1234567**
- Action: **RebootInstances**
- Status: **Success**
- Timestamp of Remediation

![](./screenshots/06-cloudwatch-remediation-logs.png)

---

# Security & Governance

## Amazon CloudWatch

Continuously monitors EC2 CPU utilization and detects sustained threshold breaches before they impact application availability.

## Amazon SNS

Acts as the event distribution service between CloudWatch Alarms and AWS Lambda, ensuring reliable notification delivery.

## AWS Lambda

Automatically performs infrastructure remediation without requiring manual intervention, reducing operational response time.

## CloudWatch Logs

Maintains a centralized audit trail for every automated remediation event, enabling monitoring, troubleshooting, and compliance reporting.

### Governance Benefits

- Automated incident detection
- Reduced Mean Time to Recovery (MTTR)
- Event-driven infrastructure remediation
- Centralized operational logging
- Improved infrastructure reliability
- Reduced manual intervention
- Repeatable self-healing architecture

---

# Technologies Used

- Amazon EC2
- Amazon CloudWatch
- CloudWatch Metrics
- CloudWatch Alarms
- CloudWatch Logs
- Amazon SNS
- AWS Lambda
- AWS Identity and Access Management (IAM)
- AWS CLI
- Python 3.12

---

# Project Deliverables

- ✅ CloudWatch Alarm Configuration
- ✅ Amazon SNS Topic Configuration
- ✅ Lambda Remediation Function
- ✅ IAM Execution Role
- ✅ Automated EC2 Recovery Workflow
- ✅ CloudWatch Log Integration
- ✅ Six AWS Console Screenshots
- ✅ Complete Project Documentation

---

# Screenshots Summary

| Screenshot | Description |
|------------|-------------|
| 01 | CloudWatch Alarm Configured |
| 02 | SNS to Lambda Subscription |
| 03 | CloudWatch CPU Utilization Graph |
| 04 | CloudWatch Alarm State (ALARM) |
| 05 | Lambda Function Execution |
| 06 | CloudWatch Remediation Logs |

---

# Project Outcome

Successfully implemented an automated incident response system that continuously monitors Amazon EC2 CPU utilization using Amazon CloudWatch. When sustained high CPU utilization is detected, a CloudWatch Alarm publishes an event to Amazon SNS, which invokes an AWS Lambda function to automatically reboot the affected EC2 instance. Every remediation event is recorded in Amazon CloudWatch Logs, providing a complete audit trail for operational monitoring and governance.

This project demonstrates practical implementation of AWS monitoring, serverless automation, event-driven architecture, and self-healing infrastructure using native AWS services to improve application availability and reduce operational effort.