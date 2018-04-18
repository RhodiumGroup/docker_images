Dockerfiles and set-up for creating a jupyterhub deployment on gce with k8s


To update this file, clone it to your local machine and make edits to the dockerfiles in the `worker` and `notebook` directories. Update the `TAG` in the `.travis.yml` file with a date in the format `yyyy-mm-dd`. If you've made multiple edits in a single day then increment up like this `yyyy-mm-dd -> yyyy-mm-dd.1`. If your build passes on Travis, it will deploy to dockerhub. From there we can deploy our helm chart. 

Any questions please email jsimcock@rhg.com
