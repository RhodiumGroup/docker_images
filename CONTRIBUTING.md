# Contributing to the compute.rhg.com docker images

## Welcome - please help!

There are two main ways to help improve these images:

1. File an issue
2. Directly make modifications to a docker file and make a pull request

And if you find these instructions or think something would be helpful,
make modifications and submit a PR! Also, additions to the test suite
including the tests specified in `notebook_test.py` would be much
appreciated!

### Making changes to a Docker file

One tricky thing about this setup is that it is extremely important that
the [notebook][] and [worker][] images match. Please make modifications to both
files so they don't get out of sync.

[notebook]: https://github.com/RhodiumGroup/docker_images/blob/master/notebook/Dockerfile
[worker]: https://github.com/RhodiumGroup/docker_images/blob/master/worker/Dockerfile


## Testing your changes

### Travis-CI

On travis, we test the containers to make sure the images build. Note that
that this is woefully insufficient for ensuring a safe deployment to the
cluster! We're looking for ways to run more comprehensive tests automatically,
but in the meantime, see the below testing strategies to really give your
changes a test drive!

The main purpose of our travis tests is actually deployment. See the
deployment section for more details.

### Set up for local testing

1.  Make sure you have docker installed and initialized

2.  Create an image locally:
    ```bash
    docker build worker -t rhodium/worker:my-tag-name
    docker build notebook -t rhodium/notebook:my-tag-name
    ```
    or pull one from dockerhub:

    ```bash
    docker pull rhodium/notebook:dev
    docker pull rhodium/worker:dev
    ```

3.  Set an environment variable to preserve this tag name, e.g.:
    ```
    NOTEBOOK_TAG=rhodium/notebook:dev
    WORKER_TAG=rhodium/worker:dev
    ```

#### Running a test suite locally

Once you've set up your machine, run the following to programatically
test the notebook:worker pairing:

```bash
# start scheduler in notebook server
docker run --net="host" -d $NOTEBOOK_TAG start.sh /opt/conda/bin/dask-scheduler --port 8786 --bokeh-port 8787 &

# at this point you could test the connection by starting a
# python session and connecting to the scheduler with
#
#     import dask.distributed as dd
#     client = dd.Client('localhost:8786')
#     client
#
# you should have a valid connection, but no workers yet

# start worker
docker run --net="host" -d $WORKER_TAG /opt/conda/bin/dask-worker localhost:8786 --worker-port 8666 --nanny-port 8785 &

# at this point, if you run `client` again, you should see
# a worker connected to the client! You can now run any
# python commands to test the connection. The rest of these
# commands attempt to establish such a connection from within
# a notebook image.

# notebook server for user connection
docker create --name tester --net="host" $NOTEBOOK_TAG

# copy test suite to test image
docker cp notebook_test.py tester:/usr/bin

# start the tester image
docker start tester

# run test suite
docker exec tester python /usr/bin/notebook_test.py
```

#### Testing the hub deployment locally

This will build a local cluster with a worker:notebook already paired.
Log into the jupyterhub cluster and make sure it works the way you expect.
Note that this does not use a kubernetes cluster, just a single worker.

```bash

# start jupyterlab in the notebook server
docker run -p 8888:8888 -p 8786:8786 -p 8787:8787 $NOTEBOOK_TAG start.sh jupyter lab --port=8888

# go to https://localhost:8888 to view the page. you'll need to enter the token from the docker log in order to log in

# open a jupyterlab terminal window and start a dask-scheduler
dask-scheduler --port 8786 --bokeh-port 8787

# in a new terminal window on your laptop, make sure you set your tag environment variables, then start a worker container using whatever worker image you want, and get it to connect to the scheduler
docker run -p 8666:8666 -p 8785:8785 --net="host" $WORKER_TAG dask-worker localhost:8786 --worker-port 8666 --nanny-port 8785

# you should see the worker report that it is registered to the scheduler, and on the scheduler terminal on jupyterlab it should report the registered worker

# in a notebook on jupyterlab, connect to the scheduler (don't create a dask cluster... the scheduler is already set up)
import dask.distributed as dd
client = dd.Client('localhost:8786')

# do whatever you want in the notebook and test the connection to the worker.
```


### Cleanup

To close & remove the images (e.g. before testing a new build):

```bash
docker stop $(docker ps -q)
docker rm $(docker ps -qa)
```


## Deployment

A worker:notebook pair is deployed to docker whenever a build is
successful on the `dev` and `master` branches.

Each worker and notebook image are tagged with one or more of several
tags:

* A version number (e.g. `0.2.1`) is assigned to each major
  release (tag). This is only pushed to docker once and is permanently
  stable. Use release tags on production deployments. To create a
  release, [draft a new release](https://github.com/RhodiumGroup/docker_images/releases/new)
  on github.

* A commit hash (e.g. `fbb4a04f3829f12c81812573c54d8e52aba324ce`) is
  assigned to every `dev` or `master` build. These are completely
  stable and will not be updated ever. Use these tags to ensure you
  always get this specific image.

* Every build on the `dev` branch will be assigned the `dev` tag. Use
  the `dev` tag to get the latest development release.

* Every build on the `master` branch will be assigned both the `dev`
  tag and the `latest` tag. Use the `latest` tag to get the latest
  stable release.

Once an image has been built and deployed to dockerhub, it can be 
tested on a test cluster. See the
[helm chart](https://github.com/RhodiumGroup/helm-chart) repo for more
information.
