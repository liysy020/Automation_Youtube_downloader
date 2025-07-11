AUTOMATION_DIR="/Automation"

until ping -c1 google.com &>/dev/null; do
  sleep 1
done
source "$AUTOMATION_DIR/bin/activate"
nohup python3 "$AUTOMATION_DIR/manage.py" runserver 127.0.0.1:8000