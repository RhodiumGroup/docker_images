# Start cluster on Google cloud
gcloud container clusters create jhub-rhg --num-nodes=2 --machine-type=n1-standard-2 --zone=us-west1-a  --cluster-version=1.9.3-gke.0

#gcloud container clusters get-credentials pangeo --zone us-central1-b --project pangeo-181919

# Set up Kubernetes
kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=jsimcock@rhg.com
kubectl --namespace kube-system create sa tiller
kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account tiller
kubectl --namespace=kube-system patch deployment tiller-deploy --type=json --patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]'

# Get Helm repositories
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

# Install JupyterHub and Dask on the cluster
helm install jupyterhub/jupyterhub --version=v0.6.0-9701a90 --name=jupyter --namespace=jhub-rhg -f jupyter-config.yml

# Look for publised services.  Route domain name A records to these IPs.
kubectl get services --namespace jhub-rhg
# Look for dask-scheduler
#      and proxy-...


# In notebooks, connect to the Dask cluster like so:
# from dask.distributed import Client
# client = Client()
# client


