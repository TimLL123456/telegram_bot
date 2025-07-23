
1. Create Access Key

2. Install AWS CLI

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