#!/bin/bash

# Exit on error
set -e

echo "Starting deployment process..."

# Create necessary directories
sudo mkdir -p /var/log/gunicorn
sudo chown -R ec2-user:ec2-user /var/log/gunicorn

# Update system packages
sudo dnf update -y
sudo dnf install -y python3.11 python3.11-pip nginx git

# Install Python environment management tools
curl https://pyenv.run | bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install Python and create virtual environment
pyenv install -s 3.11.7
pyenv global 3.11.7
python -m venv /home/ec2-user/venv

# Activate virtual environment and install dependencies
source /home/ec2-user/venv/bin/activate
python -m pip install --upgrade pip
python -m pip install uv
uv pip install -r requirements.txt

# Copy configuration files
sudo cp deploy/nginx.conf /etc/nginx/conf.d/app.conf
sudo cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service

# Set up logging
sudo mkdir -p /var/log/gunicorn
sudo chown -R ec2-user:ec2-user /var/log/gunicorn

# Reload systemd and restart services
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Deployment completed successfully!" 