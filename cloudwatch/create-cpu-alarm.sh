# create-cpu-alarm.sh
# Creates CloudWatch alarm that triggers Lambda remediation when CPU > 80% for 2 consecutive periods

aws cloudwatch put-metric-alarm \
  --alarm-name "HighCPUUtilization-AutoRemediate" \
  --alarm-description "Triggers Lambda remediation when EC2 CPU exceeds 80%" \
  --namespace "AWS/EC2" \
  --metric-name "CPUUtilization" \
  --dimensions Name=InstanceId,Value=<INSTANCE_ID> \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:<REGION>:<ACCOUNT_ID>:cpu-alarm-topic \
  --region <REGION>
