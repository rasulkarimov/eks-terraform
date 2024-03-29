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
<img width="1220" alt="image" src="https://github.com/rasulkarimov/eks-terraform/assets/53195216/d0f39535-ed3d-4c98-940d-dcd5cadf755f">

Installation time will take around ~10 minutes. 
<img width="1219" alt="image" src="https://github.com/rasulkarimov/eks-terraform/assets/53195216/633722c6-ccbf-4727-8b86-ba17f97b9cfe">


Inspect the cluster nodes and pods
~~~
kubectl get nodes
kubectl get pods -n kube-system
~~~

Get URL and heck availability. Additional time can be required for provision LoadBalanver, make sure that "nginx-lb" Service not in panding state:
~~~
kubectl get svc -n=staging
echo "http://$(kubectl get svc nginx-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'  -n=staging)"
~~~
Open on the browser:
![image](https://github.com/rasulkarimov/eks-terraform/assets/53195216/990bbeaf-2682-4e9a-b45b-8cf9fb515724)
If an Internal Server error occurs, it's more likely that the database initialization failed. For upgrading/troubleshooting, follow the "Deploy/Upgrade Application by Helm" instructions below. Otherwise, you can skip it.

## Deploy/Upgrade application by Helm 
This part is already included in Terraform with `null_resource.docker_packaging_helm_install` Below allows for manual chart updates or troubleshooting in case of any problems during Terraform installation.

During the initial installation, the 'initDb' job runs to initialize the PostgreSQL database. Ensure that this job completes successfully. If any issues arise, to rerun the job, set "myblog.initDbJob.force" to "true" in the values.yaml file and then rerun the 'helm upgrade'.

Inspect `values.yaml` File in "helm" Directory. Make sure that the correct image repositories are defined in myblog.image.repository and myblog.image.repository:
~~~
cd ../../../helm/
cat values.yaml
~~~

Authenticate into EKS cluster with the command:
~~~
aws eks update-kubeconfig --name staging --region eu-north-1
~~~

Deploy application with Helm:
~~~
helm upgrade --install --namespace=staging --create-namespace  staging ./
~~~

Inspect that pods were created:
~~~
kubectl get pods -n=staging
~~~

## Testing High Availability:
For high availability, my-blog was configured with a minimum of 2 replicas and autoscaling enabled to handle increased traffic.

To test autoscaling, use cpu_loadtest.py within a container. Trigger it by sending a GET request to /testcpu path by curl or in browser:
~~~
curl $(echo "http://$(kubectl get svc nginx-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'  -n=staging)")/testhpa
~~~

Then check HPA status and pod replicas with commands:
~~~
kubectl get hpa -n=staging
kubectl get pods -n=staging
~~~
As we can see, CPU usage increased, triggering the autoscaling of "myblog" instances:
![image](https://github.com/rasulkarimov/eks-terraform/assets/53195216/97958e1c-6548-4530-a992-00800dafe3c0)

Monitor service metrics through Grafana Dashboard. Obtain the URL for Grafana dashboard:
~~~
kubectl get svc grafana-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'  -n=monitoring
~~~

Open in your browser and log in using default credentials( admin / prom-operator ):
![image](https://github.com/rasulkarimov/eks-terraform/assets/53195216/96dd3f01-e3c3-426d-b942-b98b2d183d53)

![image](https://github.com/rasulkarimov/eks-terraform/assets/53195216/5d8c1734-5679-48a3-a615-074f3184f1ec)

From the dashboard, we can observe more detailed CPU, memory, and network metrics of our microservices.

Additionally, we should consider implementing additional application metrics. A good starting point could be the For Golden Signals, ref: https://sre.google/sre-book/monitoring-distributed-systems/

Furthermore, full CI/CD integration should be configured, including tests and security tests in the CI/CD flow.
In this demo, Nginx proxies requests to the myblog service, which, to be honest, is meaningless. Actually, "myblog" serves both front and backend, it needs to be separated, and the backend should provide an API for the front end (and possibly for other integrations). In this case, the architecture will be more scalable and maintainable. For this POC, I used a Flask project that I had on hand, on which I experimented few years ago.
