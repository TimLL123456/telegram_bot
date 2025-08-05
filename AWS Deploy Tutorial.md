# Docker

1. Build docker image for flask-app & streamlit-app in local machine
```bash
docker build -f ./Docker/dockerfile.flask -t flask-app .
```

or

```bash
docker build -f ./Docker/dockerfile.streamlit -t streamlit-app .
```

2. Push docker image to AWS ECR
```bash
docker tag [docker image name] 345345405651.dkr.ecr.ap-southeast-1.amazonaws.com/testing:streamlit-test
docker push 345345405651.dkr.ecr.ap-southeast-1.amazonaws.com/testing:streamlit-test
```

# AWS

1. Create Access Key

2. Install AWS CLI
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip
unzip awscliv2.zip
sudo ./aws/install
```

3. AWS Configure Setup
```bash
aws configure
```

4. Create Repository in ECR (Amazon Elastic Container Registry)
```bash
aws ecr create-repository --repository-name [repository name]
```

5. Login to AWS ECR through AWS CLI
```bash
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin [repository URI]
```

* `sudo usermod -aG docker ubuntu`

# Terminal

1. Get root permission
```bash
sudo su
```

2. Update apt-get
```bash
sudo apt-get update -y
```

3. Install Docker
```bash
sudo apt-get install -y docker.io docker-compose
```

4. Start and enable Docker
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

5. Install AWS CLI
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip
unzip awscliv2.zip
sudo ./aws/install
```

6. Login to AWS ECR through AWS CLI
```bash
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin [repository URI]
```

7. Pull docker image from AWS ECR
```bash
docker pull [repository URI]:[docker image name/tag]
```

8. Run docker image
* map the container’s port 8501 to a host port 8501
```bash
docker run -p 8501:8501 <image_name>
```

9. Download Ngrok
```bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok
```

10. Add Ngrok authtoken
```bash
ngrok config add-authtoken [authtoken]
```

11. Set telegram bot webhook
```bash
https://api.telegram.org/bot[telegram_bot_token]/setWebhook?url=[ngrok_url]
```

12. Deploy

* Run python script with `Screen`
```bash
screen -S flask-app
docker run -p 5000:5000 <image_name>

screen -S ngrok
ngrok http http://localhost:5000

screen -S streamlit-app
docker run -p 8501:8501 <image_name>
```

* Run docker-compose with `Screen`
```bash
screen -S tg_bot_docker_compose
sudo docker-compose up --build
```