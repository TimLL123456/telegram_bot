# Docker

1. Build docker image for flask-app & streamlit-app
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