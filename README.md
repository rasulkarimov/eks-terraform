# "Hello World"
This guide provides step-by-step instructions for provisioning a Kubernetes cluster on the AWS public cloud using Terraform and building and deploying simple "Hello World" application that exposes the following HTTP-based APIs:
~~~
Description: Saves/updates the given user’s name and date of birth in the database.
Request: PUT /hello/<username> { “dateOfBirth”: “YYYY-MM-DD” }
Response: 204 No Content 
~~~
~~~
Description: Returns hello birthday message for the given user
Request: Get /hello/<username>
Response: 200 OK
~~~

Before you begin, ensure that you have the following tools installed on your laptop: Terraform, AWS CLI, Docker, Helm, and kubectl.

Generate an AWS token and configure AWS CLI with "aws configure" or environment variables:
~~~
export AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
export AWS_DEFAULT_REGION="eu-north-1" 
~~~

## Provisioning a Kubernetes Cluster using Terraform
To get started, follow these steps:

Inspect the variable-defined files in the `terraform/projects/revolut/staging.tfvars` file:
~~~
cd terraform/projects/revolut/
cat staging.tfvars
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
The previous command should provide the public URL to the application, you can test server availability by sending GET request via "curl" or from your browser:
<img width="903" alt="image" src="https://github.com/rasulkarimov/eks-terraform/assets/53195216/9d7d0ac7-5dad-47de-894e-4a0bab5e87d3">

If an Internal Server error occurs, it's more likely that the database initialization failed. The database initialization runs only after the first installation as a post-start hook. If, for some reason, the first installation fails, then Helm should be rerun with the option "myblog.initDbJob.force: true." Alternatively, Helm should be uninstalled and then installed from scratch.
For upgrading/troubleshooting, follow the "Deploy/Upgrade Application by Helm" instructions below. Otherwise, you can skip it.

Test PUT request:
~~~
curl -X PUT -H "Content-Type: application/json" -d '{"dateOfBirth": "2000-01-01"}' http://$(kubectl get svc nginx-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'  -n=staging)/hello/johndoe
~~~

Test GET request:
~~~
curl -X GET http://$(kubectl get svc nginx-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'  -n=staging)/hello/johndoe
~~~

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

## Run/Test application locally

~~~
cd app/myblog
flask db init && flask db migrate && flask db upgrade
flask --app app --debug run
~~~ 
Send requests to API on localhost:
~~~
curl -X PUT -H "Content-Type: application/json" -d '{"dateOfBirth": "2000-01-01"}' http://127.0.0.1:5000/hello/johndoe
curl -X GET http://127.0.0.1:5000/hello/johndoe
~~~
## Destroy the cluster
Delete load balancers and destroy infrastructure with terraform:
~~~
kubectl delete svc nginx-lb  -n staging
terraform destroy -var-file=staging.tfvars
~~~
