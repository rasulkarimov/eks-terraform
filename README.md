# Full Stack MyBlog Application
This guide provides step-by-step instructions for provisioning a Kubernetes cluster using Terraform. Before you begin, ensure that you have the following tools installed on your laptop: terraform, aws, docker, helm, kubectl

## Provisioning a Kubernetes Cluster using Terraform
To get started, follow these steps:

Inspect the variable-defined files in the `terraform/projects/openinnovation/main.tf` file:
~~~
cd terraform/projects/openinnovation/
cat main.tf
~~~

Initialize Terraform, Preview changes and Apply changes:
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

Retrieve the URL and check availability. Note: Additional time may be required for LoadBalancer provisioning. Ensure that the "nginx-lb" Service is not in a pending state.
~~~
kubectl get svc -n=staging
echo "http://$(kubectl get svc nginx-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'  -n=staging)"
~~~
The previous command should provide the public URL to the application, open it on the browser:
![image](https://github.com/rasulkarimov/eks-terraform/assets/53195216/990bbeaf-2682-4e9a-b45b-8cf9fb515724)
If an Internal Server error occurs, it's more likely that the database initialization failed. The database initialization runs only after the first installation as a post-start hook. If, for some reason, the first installation fails, then Helm should be rerun with the option "myblog.initDbJob.force: true." Alternatively, Helm should be uninstalled and then installed from scratch.
For upgrading/troubleshooting, follow the "Deploy/Upgrade Application by Helm" instructions below. Otherwise, you can skip it.

## Deploy/Upgrade application by Helm 
This part is already included in Terraform with `null_resource.docker_packaging_helm_install`. The instructions below are for manually updating the application or for troubleshooting in case of any problems during Terraform installation.

During the initial installation, the 'initDbJob' job runs to initialize the PostgreSQL database. Ensure that this job completes successfully. If any issues arise, to rerun the job, set "myblog.initDbJob.force" to "true" in the values.yaml file and then rerun the 'helm upgrade'.

Inspect `values.yaml` File in "helm" Directory. Make sure that the correct image repositories are defined in myblog.image.repository and myblog.image.repository:
~~~
cd ../../../helm/
cat values.yaml
~~~

Authenticate into EKS cluster with the command(if required):
~~~
aws eks update-kubeconfig --name staging --region eu-north-1
~~~

Deploy/upgrade application with Helm:
~~~
helm upgrade --install --namespace=staging --create-namespace  staging ./
~~~

Inspect that pods are running:
~~~
kubectl get pods -n=staging
~~~

## Testing High Availability:
For high availability, my-blog was configured with a minimum of 2 replicas and autoscaling enabled to handle increased traffic.

To test autoscaling, cpu_loadtest.py script was put into the image. It can be trigger by sending a GET request to /testcpu path by curl or in browser:
~~~
curl $(echo "http://$(kubectl get svc nginx-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'  -n=staging)")/testhpa
~~~

Then check HPA status and pod replicas with commands:
~~~
kubectl get hpa -n=staging
kubectl get pods -n=staging
~~~
As we can see, CPU usage increased, this triggered the autoscaling of "myblog" instances:
![image](https://github.com/rasulkarimov/eks-terraform/assets/53195216/97958e1c-6548-4530-a992-00800dafe3c0)

Chack service metrics through Grafana Dashboard. Obtain the URL for Grafana dashboard:
~~~
kubectl get svc grafana-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'  -n=monitoring
~~~

Open in your browser and login using default credentials (admin / prom-operator)
![image](https://github.com/rasulkarimov/eks-terraform/assets/53195216/42c44b62-a6de-4211-91d6-c732a3e705e9)

![image](https://github.com/rasulkarimov/eks-terraform/assets/53195216/96dd3f01-e3c3-426d-b942-b98b2d183d53)

![image](https://github.com/rasulkarimov/eks-terraform/assets/53195216/5d8c1734-5679-48a3-a615-074f3184f1ec)

From the dashboard, we can observe more detailed CPU, memory, and network metrics of our microservices.

Moreover, it's worth considering the implementation of additional application metrics. A recommended starting point would be the Four Golden Signals, referenced here: https://sre.google/sre-book/monitoring-distributed-systems/

Furthermore, full CI/CD integration should be configured, including tests and security tests in the CI/CD flow. Optimizing management of configuration files is essential, alongside managing secret credentials through services like HashiCorp Vault or AWS Secrets Manager, for instance. Also, HTTPS has to be configured. Access to Kubernetes API has to be restricted, public access should be denied, VPN configured. And much more needs to be done.

In this demo, Nginx proxies requests to the myblog service, which, to be honest, is meaningless. Actually, "myblog" serves both front and backend, it needs to be separated, and the backend should provide an API for the frontend (and possibly for other services). In this case, the architecture will be more scalable and maintainable. For this POC, I used a Flask project that I had on hand, on which I experimented few years ago.

## Destroy the cluster
Delete load balancers and destroy infrastructure with terraform:
~~~
kubectl delete svc nginx-lb  -n staging
kubectl delete svc grafana-lb  -n monitoring
terraform destroy
~~~
