#!/usr/bin/env bash
# setup_ec2.sh - one-time setup on an Ubuntu EC2 instance.
# Author: Brittney Everson
#
# Run from inside the project folder on the server:
#   cd ~/healthcare-spending-survey && bash deploy/setup_ec2.sh
# Before running: create the .env file (cp .env.example .env, then edit it).

set -euo pipefail
APP_DIR=/home/ubuntu/healthcare-spending-survey

if [ ! -f "$APP_DIR/.env" ]; then
  echo "ERROR: $APP_DIR/.env not found. Run: cp .env.example .env  then add your MongoDB Atlas URI."
  exit 1
fi

echo "1/5 Installing system packages..."
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip nginx

echo "2/5 Creating virtual environment and installing Python packages..."
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install Flask pymongo python-dotenv gunicorn

echo "3/5 Allowing Nginx to read static files..."
chmod 755 /home/ubuntu

echo "4/5 Starting the app with systemd..."
sudo cp "$APP_DIR/deploy/survey.service" /etc/systemd/system/survey.service
sudo systemctl daemon-reload
sudo systemctl enable --now survey
sudo systemctl restart survey

echo "5/5 Configuring Nginx..."
sudo cp "$APP_DIR/deploy/nginx_survey.conf" /etc/nginx/sites-available/survey
sudo ln -sf /etc/nginx/sites-available/survey /etc/nginx/sites-enabled/survey
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

PUBLIC_IP=$(curl -s https://checkip.amazonaws.com || echo "<your-ec2-public-ip>")
echo ""
echo "Done. Open http://$PUBLIC_IP in your browser."
echo "Health check: curl http://$PUBLIC_IP/health"
