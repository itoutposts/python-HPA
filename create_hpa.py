import sys
from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()


payload = {
    "apiVersion": "autoscaling/v1",
    "kind": "HorizontalPodAutoscaler",
    "metadata": {
        "name": None,
        "namespace": "default"
    },
    "spec": {
        "maxReplicas": 5,
        "minReplicas": 1,
        "scaleTargetRef": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "name": None
        },
        "targetCPUUtilizationPercentage": 80
    }
}

v1_hpa_client = client.AutoscalingV1Api()
v1_core = client.AppsV1Api()

def create_hpa(ns: str):
    deployments = v1_core.list_namespaced_deployment(namespace=ns)
    counter = 0
    if not deployments.items:
        print(f"Deployments not found for this {ns} namespace")
    for dep in deployments.items:
        deployment_name = dep.metadata.name
        ns = dep.metadata.namespace
        print(f"Start adding HPA to {deployment_name}")
        payload["metadata"]["name"] = deployment_name
        payload["spec"]["scaleTargetRef"]["name"] = deployment_name
        try:
            v1_hpa_client.create_namespaced_horizontal_pod_autoscaler(ns,payload)
        except Exception as err:
            print(f"HPA for deployment {deployment_name} already exist")
            continue
        counter += 1
        print(f"HPA successfully added to {deployment_name}")
    print(f"Applied deployments count -> {len(deployments.items)}/{counter}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ns = sys.argv[1]
    else:
        ns = "default"
    
    print(f"executing script for namespace {ns}")
    create_hpa(ns)