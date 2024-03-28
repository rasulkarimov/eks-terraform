##############
# ECR Create
##############
resource "aws_ecr_repository" "nginx" {
	  name = "testnginx"
	  image_scanning_configuration {
			# enable scan on push
	    scan_on_push = true
	  }
}

resource "aws_ecr_repository" "myblog" {
	  name = "testmyblog"
	  image_scanning_configuration {
			# enable scan on push
	    scan_on_push = true
	  }
}
##############
# MyBlog App: build, deploy
##############
resource "null_resource" "docker_packaging_helm_install" {
	  provisioner "local-exec" {
	    command = <<EOF
	    aws ecr get-login-password --region "${var.region}" | docker login --username AWS --password-stdin "${aws_ecr_repository.myblog.repository_url}"
      docker build -f ../../../app/myblog/Dockerfile -t "${aws_ecr_repository.myblog.repository_url}:0.0.1"
      docker push "${aws_ecr_repository.myblog.repository_url}:0.0.1"
      aws ecr get-login-password --region "${var.region}" | docker login --username AWS --password-stdin "${aws_ecr_repository.nginx.repository_url}"
      docker build -f ../../../app/nginx/Dockerfile -t "${aws_ecr_repository.nginx.repository_url}:0.0.1"
      docker push "${aws_ecr_repository.nginx.repository_url}:0.0.1"
      echo "Helm install MyBlog App"
      aws eks update-kubeconfig --name "${var.cluster_name}" --region "${var.region}"
      helm upgrade --install \
      --set=myblog.image.repository="${aws_ecr_repository.myblog.repository_url}" \
      --set=nginx.image.repository="${aws_ecr_repository.nginx.repository_url}" \
      --namespace=staging --create-namespace  "${var.environment}" ../../../helm
	    EOF
	  }

	  triggers = {
	    "run_at" = timestamp()
	  }
	
	  depends_on = [
	    aws_ecr_repository.myblog,
      aws_eks_cluster.dev
	  ]
}