# KubeShift Engine

**Cloud-Native Migration & Provisioning Control**

A sophisticated Kubernetes-to-OpenShift migration framework that intelligently translates cloud-native application blueprints and orchestrates multi-platform deployments with enterprise-grade security compliance.

---

## 🎯 Overview

KubeShift Engine is a declarative infrastructure-as-code solution designed to bridge the gap between standard Kubernetes environments (GKE) and enterprise-grade platforms (Red Hat OpenShift/ROSA/ARO). It automates the tedious process of manifest translation, platform-specific optimization, and cluster deployment using a single command.

### Key Capabilities

- **Intelligent Template Translation**: Automatically converts standard Kubernetes manifests into platform-optimized configurations
- **Multi-Platform Support**: Deploy the same application to GKE and OpenShift from a single source blueprint
- **Enterprise Security**: Enforces non-root user execution, security contexts, and compliance best practices
- **Graceful Fallbacks**: Applications adapt to missing dependencies (e.g., Redis cache) without failure
- **Automated Validation**: Offline staging simulations verify compatibility before live deployment

---

## 🏗️ Architecture Components

### 1. Application Layer (`app/` folder)

#### `app.py` - Flask Microservice
A dual-mode Python Flask web service that:
- Tracks page views using a Redis cache backend
- Automatically increments hit counters when Redis is available
- Gracefully degrades to standalone mode if Redis connection fails
- Exposes metrics on the `/` route at port 8080

**Network Dependencies**:
- `REDIS_HOST`: Redis service endpoint (default: `localhost`)
- `REDIS_PORT`: Redis port (default: `6379`)

#### `Dockerfile` - Enterprise-Hardened Container
A security-first containerization strategy:
- Runs as non-root USER `1001` (not `0`)
- Grants group-write permissions (`chmod g+w`) for OpenShift dynamic UID assignment
- Uses Python 3 slim base image for minimal attack surface
- Exposes port 8080 (safe for restricted users)

**Security Benefits**:
- Passes strict corporate security admission controllers
- Compatible with OpenShift's Security Context Constraints (SCC)
- Prevents accidental privilege escalation

### 2. Source Template (`manifests/k8s-app-template.yaml`)

A multi-document Kubernetes manifest declaring:
- **2-Replica Flask Frontend Deployment**: Load-balanced web tier
- **Flask ClusterIP Service**: Internal service discovery
- **Standard Ingress**: Public internet exposure (for GKE)
- **1-Replica Redis Backend**: In-cluster caching database
- **Redis Service**: Backend service discovery

The template uses `TARGET_IMAGE_PLACEHOLDER` as a dynamic injection point for container registry paths.

### 3. Translation Engine (`engine.py`)

The intelligent compiler that:
- Reads raw Kubernetes blueprints using PyYAML
- Detects structural objects and platform-specific requirements
- Generates two distinct platform distributions in the `dist/` folder

**GKE Bundle Generation**:
- Injects your live Google Artifact Registry image path
- Preserves standard Kubernetes Ingress networking
- Ready for immediate deployment to GKE clusters

**OpenShift Bundle Generation**:
- Replaces standard Ingress with OpenShift-native Route objects
- Injects explicit `runAsNonRoot: true` security context
- Compatible with Red Hat's built-in HAProxy routers
- Enforces enterprise compliance policies

**Output Files**:
```
dist/
├── gke-deployment.yaml          # GKE-optimized manifest bundle
└── openshift-deployment.yaml    # OpenShift-optimized manifest bundle
```

### 4. Orchestration & Automation

#### `main.py` - Master Control Plane
The entry point orchestrating the entire migration lifecycle:
1. Queries Google Cloud metadata to extract your active Project ID
2. Constructs the Artifact Registry container image path (`europe-west4-docker.pkg.dev/{project-id}/kubeshift-repo/flask-app:v1`)
3. Invokes the Python translation engine to generate platform bundles
4. Sequentially spawns Ansible deployment workers

#### `ansible/deploy-gke.yml` - GKE Worker
Automated GKE deployment orchestration:
- Authenticates to live GKE cluster using gcloud-auth-plugin tokens
- Creates or verifies the `kubeshift-gke` namespace
- Uses `kubernetes.core` module for native cluster API communication
- Deploys 2x Flask frontend pods + 1x Redis backend
- Auto-provisions resources with strict interpreter isolation

#### `ansible/deploy-openshift.yml` - OpenShift Worker
Enterprise compliance validation and staging:
- Performs offline schema validation of OpenShift artifacts
- Verifies presence of `kind: Route` configurations
- Asserts `runAsNonRoot: true` security policies
- Generates readiness reports for ROSA/ARO migration
- Simulates deployment without modifying live clusters

---

## 🔄 Execution Lifecycle

### Step-by-Step Process

```
[Source Blueprint]
       ↓
[Python Translation Engine]
       ↓
    💾 Generated dist/ Assets
       ├─→ gke-deployment.yaml
       └─→ openshift-deployment.yaml
            ↓
    ┌───────┴───────┐
    ↓               ↓
[GKE Playbook]  [OpenShift Playbook]
    ↓               ↓
Cluster       Validation &
Deployment    Compliance Check
```

### Detailed Breakdown

#### Phase 1: Compilation & Parsing

1. **Project Discovery**
   - `main.py` queries Google Cloud metadata server
   - Extracts your active Project ID automatically
   
2. **Image Path Construction**
   - Builds absolute container registry path: `europe-west4-docker.pkg.dev/{project-id}/kubeshift-repo/flask-app:v1`

3. **Template Translation**
   - `engine.py` parses multi-document YAML template
   - Executes search-and-replace to swap placeholder with real registry path
   - Generates two platform-optimized variants

#### Phase 2: Live GKE Deployment

1. **Worker Initialization**
   - `main.py` triggers `ansible/deploy-gke.yml`
   - Ansible binds Python interpreter to virtual environment

2. **Cluster Authentication**
   - Uses gcloud-auth-plugin to generate cluster tokens
   - Establishes connection to GKE control plane

3. **Resource Provisioning**
   - Checks for `kubeshift-gke` namespace (creates if missing)
   - Pushes `gke-deployment.yaml` to cluster
   - GKE scheduler places workloads on worker nodes
   - Container images pulled from Artifact Registry
   - 2x Flask pods and 1x Redis pod start in production mode

#### Phase 3: OpenShift Staging Simulation

1. **Artifact Validation**
   - `ansible/deploy-openshift.yml` executes offline analysis
   - Scans `openshift-deployment.yaml` for structural correctness

2. **Compliance Verification**
   - Confirms presence of OpenShift-native Route objects
   - Verifies `runAsNonRoot: true` security enforcement
   - Validates enterprise compliance metrics

3. **Readiness Assessment**
   - Generates migration readiness report
   - Confirms artifacts are prepared for ROSA/ARO deployment
   - Prevents live API resource mismatches

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Google Cloud SDK (`gcloud` CLI)
- Ansible 2.9+
- kubectl configured for GKE cluster access
- Virtual environment (`venv`)

### Installation

```bash
# Clone the repository
git clone https://github.com/JeeT-Suhrid2003/kubeshift-engine.git
cd kubeshift-engine

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Ansible collections
ansible-galaxy collection install kubernetes.core
```

### Execution

```bash
# Run the full migration pipeline
python3 main.py

# Expected output:
# ================================================================
#       KUBESHIFT: CLOUD-NATIVE MIGRATION & PROVISIONING CONTROL   
# ================================================================
# [Step 1/3] Initiating configuration translation framework...
# [Step 2/3] Executing declarative GKE configuration tracking...
# [Step 3/3] Executing OpenShift Target Migration...
# [✓] Migration cycle validation complete.
```

---

## 📁 Project Structure

```
kubeshift-engine/
├── main.py                              # Master control plane orchestrator
├── engine.py                            # Python translation engine (PyYAML compiler)
├── requirements.txt                     # Python dependencies
├── app/
│   ├── app.py                           # Flask microservice (dual-mode)
│   ├── Dockerfile                       # Enterprise-hardened container image
│   └── requirements.txt                 # Flask + Redis Python dependencies
├── manifests/
│   └── k8s-app-template.yaml           # Multi-document Kubernetes blueprint
├── ansible/
│   ├── deploy-gke.yml                   # GKE deployment playbook
│   └── deploy-openshift.yml             # OpenShift validation playbook
└── dist/                                # Generated platform-optimized bundles
    ├── gke-deployment.yaml              # GKE-ready manifest
    └── openshift-deployment.yaml        # OpenShift-ready manifest
```

---

## 🔐 Security Features

### Non-Root Execution
All containers enforce `USER 1001` (non-root) with explicit security contexts preventing privilege escalation.

### Security Context Constraints (SCC)
- OpenShift bundle includes `runAsNonRoot: true` enforcement
- Group-writable permissions allow OpenShift's dynamic UID assignment
- Compliant with corporate security admission controllers

### Graceful Error Handling
- Flask app detects Redis connection failures and degrades gracefully
- No hard dependency failures; system continues in standalone mode

### Offline Validation
- OpenShift playbook performs schema validation before live deployment
- Prevents API resource mismatches in production environments

---

## 📊 Deployment Topology

### GKE Cluster (Kubernetes)
```
Namespace: kubeshift-gke
├── Flask Frontend (2 replicas)
│   ├── Pod 1 (port 8080)
│   └── Pod 2 (port 8080)
├── Flask Service (ClusterIP, port 80)
├── Ingress Controller (external exposure)
└── Redis Backend (1 replica, port 6379)
```

### OpenShift Cluster (Red Hat Enterprise)
```
Namespace: kubeshift-openshift
├── Flask Frontend (2 replicas)
│   ├── Pod 1 (port 8080, USER 1001)
│   └── Pod 2 (port 8080, USER 1001)
├── Flask Service (port 80)
├── Route (HAProxy-backed, external exposure)
└── Redis Backend (1 replica, port 6379)
```

---

## 🔧 Configuration

### Environment Variables

**GKE Configuration**:
- `REDIS_HOST`: Redis service endpoint (default: `redis-service`)
- `REDIS_PORT`: Redis port (default: `6379`)

**Cloud Configuration**:
- Automatically detected from `gcloud config get-value project`
- Artifact Registry path: `europe-west4-docker.pkg.dev/{project-id}/kubeshift-repo/flask-app:v1`

**Ansible Configuration**:
- `manifest_path`: Location of generated manifests (auto-configured)
- `k8s_namespace`: Target namespace (GKE: `kubeshift-gke`, OpenShift: `kubeshift-openshift`)

---

## 📝 Generated Manifests

### GKE Deployment Bundle
- Standard Kubernetes Ingress for public access
- Real container image paths from your Artifact Registry
- Native GKE networking semantics

### OpenShift Deployment Bundle
- OpenShift Route objects (HAProxy-backed)
- Explicit `runAsNonRoot: true` security context
- Enterprise compliance policies embedded
- Ready for ROSA (Red Hat OpenShift on AWS) or ARO (Azure Red Hat OpenShift)

---

## 🐛 Troubleshooting

### Redis Connection Timeout
If the Flask app shows "Connected to Redis, but timed out":
- Verify Redis pod is running in the cluster
- Check network policies and service discovery
- App will continue in standalone mode

### Manifest Not Found
If Ansible fails with manifest path error:
- Ensure `engine.py` completed successfully
- Verify `dist/` folder exists with generated files
- Check file permissions in working directory

### GKE Authentication Failed
If Ansible cannot connect to cluster:
- Run `gcloud auth application-default login`
- Verify cluster credentials: `gcloud container clusters get-credentials {cluster-name}`
- Ensure service account has adequate permissions

### OpenShift Validation Failed
If schema validation fails:
- Check that `kind: Route` objects are present in generated manifest
- Verify `runAsNonRoot: true` is in deployment spec
- Run `grep` commands manually to debug

---

## 📚 Dependencies

**Python Packages**:
- `PyYAML`: Kubernetes manifest parsing and generation
- `Flask`: Microservice framework
- `redis`: Cache backend connectivity
- `ansible`: Infrastructure orchestration
- `kubernetes`: Native Kubernetes API communication

**Ansible Collections**:
- `kubernetes.core`: Kubernetes module support

---

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional platform support (EKS, AKS)
- Advanced networking configurations
- Multi-region deployment strategies
- Custom security policies
- CI/CD pipeline integration

---

## 📄 License

This project is part of the cloud-native ecosystem. Please refer to LICENSE file for details.

---

## 🔗 References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Red Hat OpenShift Documentation](https://docs.openshift.com/)
- [Google Kubernetes Engine Docs](https://cloud.google.com/kubernetes-engine/docs)
- [Ansible Kubernetes Collection](https://docs.ansible.com/ansible/latest/collections/kubernetes/core/)
- [PyYAML Documentation](https://pyyaml.org/)

---

## 📞 Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Check existing documentation and FAQs
- Review deployment logs for detailed error messages

---

**Last Updated**: June 8, 2026  
**Repository**: [JeeT-Suhrid2003/kubeshift-engine](https://github.com/JeeT-Suhrid2003/kubeshift-engine)
