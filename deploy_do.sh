# Deployment script for CRIM Streamlit app on Digital Ocean
# Run this on your droplet after SSH login
# This script creates a virtual environment automatically

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip (if not already)
sudo apt install python3 python3-pip python3-venv -y

# Create app directory
mkdir -p ~/crim_app
cd ~/crim_app

# Clone the repo (replace with your repo URL)
git clone https://github.com/yourusername/CRIM_Streamlit.git .
# Or if private: git clone https://username:token@github.com/yourusername/CRIM_Streamlit.git .

# Create virtual environment (this isolates the app's dependencies)
python3 -m venv crim_env
source crim_env/bin/activate

# Install requirements
pip install -r requirements.txt

# Test run (optional - run in background or separate terminal)
# streamlit run app_22.py --server.port 8501 --server.address 0.0.0.0

# For production, create systemd service
sudo tee /etc/systemd/system/crim-streamlit.service > /dev/null <<EOF
[Unit]
Description=CRIM Streamlit App
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER/crim_app
ExecStart=/home/$USER/crim_app/crim_env/bin/streamlit run app_22.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable crim-streamlit
sudo systemctl start crim-streamlit

# Check status
sudo systemctl status crim-streamlit

# Install nginx for reverse proxy (if not already)
sudo apt install nginx -y

# Configure nginx
sudo tee /etc/nginx/sites-available/crim-app > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or droplet IP

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/crim-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# For SSL (optional, using Let's Encrypt)
# sudo apt install certbot python3-certbot-nginx -y
# sudo certbot --nginx -d your-domain.com

# To update the app:
# cd ~/crim_app
# git pull
# source crim_env/bin/activate
# pip install -r requirements.txt  # if requirements changed
# sudo systemctl restart crim-streamlit

# To update data (if needed):
# python3 -c "
# import requests, json
# obs_data = requests.get('https://crimproject.org/data/observations').json()
# json.dump(obs_data, open('crim_data/crim_obs.json', 'w'))
# rels_data = requests.get('https://crimproject.org/data/relationships').json()
# json.dump(rels_data, open('crim_data/crim_rels.json', 'w'))
# "
# sudo systemctl restart crim-streamlit