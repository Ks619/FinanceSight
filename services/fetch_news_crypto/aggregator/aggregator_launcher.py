import subprocess
import asyncio
from main import orchestrate_and_save_news

# List of microservice names (matching YAML file names and Service names in Kubernetes)
SERVICES = ["service_1", "service_2", "service_3"]

def apply_k8s_yaml(service_name: str):
    """
    Applies the deployment and service YAML for a given microservice using kubectl.
    """
    print(f"Applying {service_name}...")
    subprocess.run(["kubectl", "apply", "-f", f"{service_name}-deployment.yaml"])
    subprocess.run(["kubectl", "apply", "-f", f"{service_name}-service.yaml"])

def delete_k8s_yaml(service_name: str):
    """
    Deletes the deployment and service YAML for a given microservice using kubectl.
    """
    print(f"Deleting {service_name}...")
    subprocess.run(["kubectl", "delete", "-f", f"{service_name}-deployment.yaml"])
    subprocess.run(["kubectl", "delete", "-f", f"{service_name}-service.yaml"])

async def run_aggregator_with_services():
    """
    Applies all services, waits for them to become ready, runs the aggregator,
    and then cleans up by deleting the services.
    """
    try:
        # Apply all service deployments
        for service in SERVICES:
            apply_k8s_yaml(service)

        # Run the main aggregation logic (includes waiting for services internally)
        print("Running aggregator logic...")
        result = await orchestrate_and_save_news()

        print("Aggregator finished.")
        print(result)

    finally:
        # Clean up services even if something fails
        for service in SERVICES:
            delete_k8s_yaml(service)

if __name__ == "__main__":
    asyncio.run(run_aggregator_with_services())
