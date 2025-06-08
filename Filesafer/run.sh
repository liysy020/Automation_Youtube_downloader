#!/bin/bash

AUTOMATION_DIR="/Automation"
LOG_DIR="$AUTOMATION_DIR/logs"

# Create log directory if missing
#mkdir -p "$LOG_DIR"

# Wait for network connectivity (critical for SSL/certificates)
until ping -c1 google.com &>/dev/null; do
  sleep 1
done

# Activate the virtual environment
source "$AUTOMATION_DIR/bin/activate"

# Run Filestore server on port 8000
python3 "$AUTOMATION_DIR/Filestore/manage.py" runsslserver \
  --cert "$AUTOMATION_DIR/Cert/Automation.cer" \
  --key "$AUTOMATION_DIR/Cert/Private.key" \
  0.0.0.0:8000 &

exit 0
