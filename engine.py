import yaml
import os
import sys

def translate_manifests(source_file, target_image):
    print(f"[*] Reading source Kubernetes manifest: {source_file}")
    
    with open(source_file, 'r') as f:
        # Load all YAML documents from the multi-document template file
        documents = list(yaml.load_all(f, Loader=yaml.FullLoader))
    
    k8s_output = []
    openshift_output = []
    
    for doc in documents:
        if not doc:
            continue
            
        # Deep copy the document to separate K8s and OpenShift mutations
        doc_str = yaml.dump(doc)
        k8s_doc = yaml.load(doc_str, Loader=yaml.FullLoader)
        oc_doc = yaml.load(doc_str, Loader=yaml.FullLoader)
        
        # 1. Update image placeholder for both platforms
        if k8s_doc.get('kind') == 'Deployment' and k8s_doc['metadata']['name'] == 'flask-frontend':
            k8s_doc['spec']['template']['spec']['containers'][0]['image'] = target_image
            oc_doc['spec']['template']['spec']['containers'][0]['image'] = target_image
            
            # Enforce OpenShift security best practices explicitly in the manifest
            # OpenShift restricts running as arbitrary root IDs unless specifically constrained
            oc_doc['spec']['template']['spec']['securityContext'] = {
                'runAsNonRoot': True
            }
            
        # 2. Translate Ingress to OpenShift Route
        if doc.get('kind') == 'Ingress':
            # Skip adding standard Ingress to the OpenShift manifest array
            print("[+] Converting Ingress asset 'frontend-ingress' to OpenShift 'Route' topology...")
            
            oc_route = {
                'apiVersion': 'route.openshift.io/v1',
                'kind': 'Route',
                'metadata': {
                    'name': doc['metadata']['name'],
                    'labels': {
                        'app': 'flask-frontend'
                    }
                },
                'spec': {
                    'to': {
                        'kind': 'Service',
                        'name': 'flask-service',
                        'weight': 100
                    },
                    'port': {
                        'targetPort': 8080
                    },
                    'wildcardPolicy': 'None'
                }
            }
            openshift_output.append(oc_route)
            k8s_output.append(k8s_doc)
        else:
            k8s_output.append(k8s_doc)
            openshift_output.append(oc_doc)

    # Save target specific distributions
    os.makedirs('dist', exist_ok=True)
    
    with open('dist/gke-deployment.yaml', 'w') as f:
        yaml.dump_all(k8s_output, f, default_flow_style=False)
    print("[✓] Successfully compiled GKE deployment bundle: dist/gke-deployment.yaml")
        
    with open('dist/openshift-deployment.yaml', 'w') as f:
        yaml.dump_all(openshift_output, f, default_flow_style=False)
    print("[✓] Successfully compiled OpenShift optimized bundle: dist/openshift-deployment.yaml")

if __name__ == "__main__":
    # Fetch current Project ID to map image path
    project_id = os.popen('gcloud config get-value project').read().strip()
    image_path = f"europe-west4-docker.pkg.dev/{project_id}/kubeshift-repo/flask-app:v1"
    
    translate_manifests('manifests/k8s-app-template.yaml', image_path)
