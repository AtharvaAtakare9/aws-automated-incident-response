#!/bin/bash
# generate-load.sh - stress CPU on the target EC2 instance to trigger alarm
# run this ON the EC2 instance (via SSH/SSM)

sudo amazon-linux-extras install epel -y 2>/dev/null || sudo apt-get install -y stress
stress --cpu 4 --timeout 600
# Runs 4 CPU workers for 10 minutes -> should push CPUUtilization above 80% threshold
