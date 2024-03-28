#openshift
oc get template postgresql-ephemeral -n openshift -o json > postgres.json

oc process -f postgres.json -p POSTGRESQL_USER=postgres1 -p POSTGRESQL_PASSWORD=postgres1 -p POSTGRESQL_DATABASE=posts_api -p DATABASE_SERVICE_NAME=postgres -l app=postgres | oc create -f -

oc new-app --as-deployment-config --name flask https://github.com/rasulkarimov/python --context-dir flask_blog_on_postgres_openshift/app/

#db initialization
oc exec $(oc get pods -l deployment=flask-1 -o jsonpath='{..metadata.name}') -it -- flask db init
oc exec $(oc get pods -l deployment=flask-1 -o jsonpath='{..metadata.name}') -it -- flask db migrate
oc exec $(oc get pods -l deployment=flask-1 -o jsonpath='{..metadata.name}') -it -- flask db upgrade
#db initialization by  post-deployment life-cycle execution
oc patch dc/flask --patch '{"spec":{"strategy":{"recreateParams":{"post":{"failurePolicy": "Ignore","execNewPod":{"containerName":"flask","command":["/bin/sh","-c","flask db init 2>/dev/null&&flask db migrate 2>/dev/null&&flask db upgrade 2>/dev/null"]}}}}}}'

oc new-app --as-deployment-config --name nginx https://github.com/rasulkarimov/python --context-dir flask_blog_on_postgres_openshift/nginx/

