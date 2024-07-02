# Networking 
region = "eu-north-1"
vpc_cidr = "10.0.0.0/16"
private_subnet_1 = "10.0.0.0/19"
private_subnet_2 = "10.0.32.0/19"
private_subnet_3 = "10.0.128.0/19"
public_subnet_1  = "10.0.64.0/19"
public_subnet_2  = "10.0.96.0/19"
public_subnet_3  = "10.0.160.0/19"
# EKS Cluster
cluster_name = "staging"
cluster_version = "1.28"
environment = "staging"
# Nodes Autoscaling desired instance size
instance_types = "t3.small"
desired_size = 2
max_size = 5
min_size = 2
max_unavailable = 1

alb_ingress = "1.6.1"
alb_ingress_image_tag = "v2.6.1"
csi_driver = "v1.26.0-eksbuild.1"
enable_cluster_log_types = ["api", "authenticator", "audit", "scheduler", "controllerManager"]

