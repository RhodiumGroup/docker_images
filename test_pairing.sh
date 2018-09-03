#!/usr/bin/env bash

set -e

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
docker run --net="host" -d $WORKER_TAG dask-worker localhost:8786 --worker-port 8666 --nanny-port 8785 &

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

echo "closing containers"
docker stop $(docker ps -q);
docker rm $(docker ps --all -q);

echo "done"