#!/bin/bash

AUTOMATION_DIR="/Automation"

# Wait for network connectivity (critical for SSL/certificates)
until ping -c1 google.com &>/dev/null; do
  sleep 1
done

# Activate the virtual environment
source "$AUTOMATION_DIR/bin/activate"

# Run Filestore server on port 8000
python3 "$AUTOMATION_DIR/manage.py" runsslserver \
  --cert "$AUTOMATION_DIR/Cert/Automation.cer" \
  --key "$AUTOMATION_DIR/Cert/Private.key" \
  0.0.0.0:8000 &

exit 0
