# Full Stack MyBlog Application
This guide provides step-by-step instructions for provisioning a Kubernetes cluster using Terraform. Before you begin, ensure that you have the following tools installed on your laptop: terraform, aws, docker, helm, kubectl

## Provisioning a Kubernetes Cluster using Terraform
To get started, follow these steps:

Inspect the variable-defined files in the `terraform/projects/openinnovation/main.tf` file:
~~~
cd terraform/projects/openinnovation/
cat main.tf
~~~

Install infrustructure:
~~~
terraform init
terraform plan -var-file=staging.tfvars
terraform apply -var-file=staging.tfvars
~~~

Installation time will take around ~10 minutes. When EKS cluster installed, authenticate into EKS cluster with command:
~~~
aws eks update-kubeconfig --name staging --region eu-north-1
~~~

Inspect the cluster nodes and pods
~~~
kubectl get nodes
kubectl get pods -n kube-system
~~~

Get URL and heck availability on browser. Additional time can be required for provision LoadBalanver, make sure that "nginx-lb" Service not in panding state:
~~~
kubectl get svc -n=staging
echo "http://$(kubectl get svc nginx-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'  -n=staging)"
~~~

## Deploy application by Helm 
This part is already included in Terraform with `null_resource.docker_packaging_helm_install` Below allows for manual chart updates or troubleshooting in case of any problems during Terraform installation.

Inspect `values.yaml` File in "helm" Directory. Make sure that the correct image repositories are defined in myblog.image.repository and myblog.image.repository:
~~~
cd ../../../helm/
cat values.yaml
~~~
Deploy application with Helm:
~~~
helm upgrade --install --namespace=staging --create-namespace  staging ./
~~~

Inspect that pods were created:
~~~
kubectl get pods -n=staging
~~~

During the initial installation, the 'initDb' job runs to initialize the PostgreSQL database. Ensure that this job completes successfully. If any issues arise, to rerun the job, set "myblog.initDbJob.force" to "true" in the values.yaml file and then rerun the 'helm upgrade' command.
