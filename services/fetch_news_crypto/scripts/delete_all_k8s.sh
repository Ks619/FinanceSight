#!/bin/bash

echo "Deploying all Kubernetes manifests..."
kubectl apply -f ../k8s_manifests/
echo "Deployment complete!"
