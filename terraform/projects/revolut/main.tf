module "eks" {
  source = "../../modules/eks" 
  # Networking 
  region           = var.region
  vpc_cidr         = var.vpc_cidr
  private_subnet_1 = var.private_subnet_1
  private_subnet_2 = var.private_subnet_2
  private_subnet_3 = var.private_subnet_3
  public_subnet_1  = var.public_subnet_1
  public_subnet_2  = var.public_subnet_2
  public_subnet_3  = var.public_subnet_3
  # EKS Cluster
  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version
  environment     = var.environment
  # Nodes Autoscaling desired instance size
  instance_types  = var.instance_types
  desired_size    = var.desired_size
  max_size        = var.max_size
  min_size        = var.min_size
  max_unavailable = var.max_unavailable

  alb_ingress           = var.alb_ingress
  alb_ingress_image_tag = var.alb_ingress_image_tag

  # ALB Ingress Controller and External DNS 
  # external_dns          = var.external_dns

  # Route53 Domain
  # domain         = var.domain
  # hosted_zone_id = var.hosted_zone_id

  # csi driver
  csi_driver = var.csi_driver
  # Logs
  enable_cluster_log_types = var.enable_cluster_log_types
}
output "eks" {
  value = module.eks.eks
}