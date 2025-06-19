#!/bin/bash

echo "Applying all manifests from k8s_manifests/..."

kubectl apply -f ../k8s_manifests/

echo "All Kubernetes resources applied!"
