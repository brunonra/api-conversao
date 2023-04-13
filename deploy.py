import os
from kubernetes import client, config
from github import Github

# Load the Kubernetes configuration from the specified kubeconfig file
kubeconfig_file = os.environ['KUBECONFIG']
config.load_kube_config(kubeconfig_file)

# Authenticate to the GitHub API using the specified GitHub API token
github_token = os.environ['GITHUB_TOKEN']
gh = Github(github_token)

# Get the GitHub repository information for the repository that was cloned in the previous step
repo_name = os.environ['GITHUB_REPOSITORY']
repo = gh.get_repo(repo_name)

# Get the latest release tag for the GitHub repository
latest_release = repo.get_latest_release()
image_tag = latest_release.tag_name

# Create a Kubernetes deployment object with the specified Docker image and image tag
deployment = client.V1Deployment(
    metadata=client.V1ObjectMeta(name='your-deployment'),
    spec=client.V1DeploymentSpec(
        selector=client.V1LabelSelector(
            match_labels={'app': 'your-app'}
        ),
        replicas=1,
        template=client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={'app': 'your-app'}
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name='your-container',
                        image='your-registry/your-image:{}'.format(image_tag),
                        ports=[client.V1ContainerPort(container_port=80)]
                    )
                ]
            )
        )
    )
)

# Create a Kubernetes service object for the deployment
service = client.V1Service(
    metadata=client.V1ObjectMeta(name='your-service'),
    spec=client.V1ServiceSpec(
        selector={'app': 'your-app'},
        ports=[client.V1ServicePort(port=80, target_port=80)]
    )
)

# Create the deployment and service in Kubernetes
apps_v1 = client.AppsV1Api()
api_v1 = client.CoreV1Api()
deployment = apps_v1.create_namespaced_deployment(body=deployment, namespace='default')
service = api_v1.create_namespaced_service(body=service, namespace='default')

print('Deployment and service created successfully.')
