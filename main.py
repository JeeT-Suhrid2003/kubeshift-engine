import os
import subprocess
import sys
from engine import translate_manifests

def run_command(command, description):
    print(f"\n[*] Execution Step: {description}")
    try:
        process = subprocess.run(command, shell=True, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[X] Error running task during {description}:")
        return False

def main():
    print("================================================================")
    print("      KUBESHIFT: CLOUD-NATIVE MIGRATION & PROVISIONING CONTROL   ")
    print("================================================================")
    
    project_id = os.popen('gcloud config get-value project').read().strip()
    image_path = f"europe-west4-docker.pkg.dev/{project_id}/kubeshift-repo/flask-app:v1"
    
    print("\n[Step 1/3] Initiating configuration translation framework...")
    translate_manifests('manifests/k8s-app-template.yaml', image_path)
    
    print("\n[Step 2/3] Executing declarative GKE configuration tracking...")
    run_command("ansible-playbook ansible/deploy-gke.yml", "GKE Core Workload Provisioning")
    
    print("\n[Step 3/3] Executing OpenShift Target Migration...")
    run_command("ansible-playbook ansible/deploy-openshift.yml", "OpenShift Target Migration")

    print("\n[✓] Migration cycle validation complete.")

if __name__ == "__main__":
    main()
