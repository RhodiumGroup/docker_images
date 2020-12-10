**NOTE:** This repo has been **moved** to https://gitlab.com/rhodium/infra_management/google/jupyterhub-images/docker_images/-/tree/master

[![build status](https://travis-ci.org/RhodiumGroup/docker_images.svg?branch=master)](https://travis-ci.org/RhodiumGroup/docker_images) [![notebook pulls](https://img.shields.io/docker/pulls/rhodium/notebook.svg?label=notebook%20pulls)](https://hub.docker.com/r/rhodium/notebook/) [![notebook image metadata](https://images.microbadger.com/badges/image/rhodium/notebook.svg)](https://microbadger.com/images/rhodium/notebook "notebook image metadata") [![worker pulls](https://img.shields.io/docker/pulls/rhodium/worker.svg?label=worker%20pulls)](https://hub.docker.com/r/rhodium/worker/) [![worker image metadata](https://images.microbadger.com/badges/image/rhodium/worker.svg)](https://microbadger.com/images/rhodium/worker "worker image metadata")

Dockerfiles and set-up for creating a jupyterhub deployment on gce with k8s


To update this file

1. Clone it to your local machine
2. Create a new branch
3. Make edits to the dockerfiles in the `worker` and `notebook` directories.  
4. Commit your changes
5. Tag your image with `python bump.py`
6. Push to github and make a pull request to master
7. If your build passes on Travis, we'll merge it and it will deploy to dockerhub

Any questions please email mdelgado@rhg.com

# Cluster overview

* compute.rhg.com: flagship Rhodium compute cluster
* impactlab.rhg.org: flagship Climate Impact Lab compute cluster

Preemptable clusters:

* coastal.rhg.com: pods in this cluster are cheaper but can disappear at any time. expect less stability, more bugs, popup errors, and lower bills.

Testing clusters:

* compute-test.rhg.com: staging deployment with stable users & user directories. This cluster should be used to beta-test deployments scheduled for the production servers in an environment similar to production. users should not expect their data here to be safe, but admins should make an effort to simulate production roll-outs and to ensure data/user safety in upgrading the cluster. admins should encourage production users to test their workflows on this cluster before a major production upgrade.
* testing.climate-kube.com: bleeding-edge test cluster. absolutely no guarantee of data/user/environment preservation. users should expect the entire cluster to be deleted at any point.
* test2.climate-kube.com: same purpose as testing.climate-kube.com, but another one to parallelize the madness.
