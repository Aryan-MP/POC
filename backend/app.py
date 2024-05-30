from flask import Flask, request, jsonify
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/deploy', methods=['POST'])
def deploy():
    data = request.json
    template_url = data.get('https://cloudcrowd.s3.ap-south-1.amazonaws.com/main.tf')
    
    if not template_url:
        return jsonify({'message': 'Template URL is required'}), 400
    
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')
    region = os.getenv('REGION')
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = 'aryan-rg-test'
    container_group_name = 'aryan-container-group'
    container_image = 'afzal006/my-terraform-image'
    
    credentials = DefaultAzureCredential()
    client = ContainerInstanceManagementClient(credentials, subscription_id)
    
    container_group = {
        "location": region,
        "containers": [
            {
                "name": container_group_name,
                "image": container_image,
                "resources": {
                    "requests": {
                        "cpu": 1,
                        "memory_in_gb": 1.5
                    }
                },
                "environment_variables": [
                    {"name": "ACCESS_KEY", "value": access_key},
                    {"name": "SECRET_KEY", "value": secret_key},
                    {"name": "REGION", "value": region},
                    {"name": "TEMPLATE_URL", "value": template_url}
                ]
            }
        ],
        "os_type": "Linux",
        "restart_policy": "Never"
    }
    
    try:
        client.container_groups.begin_create_or_update(resource_group, container_group_name, container_group)
        return jsonify({'message': 'Deployment started successfully'})
    except Exception as e:
        return jsonify({'message': 'Failed to deploy container', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
