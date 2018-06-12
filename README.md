Dockerfiles and set-up for creating a jupyterhub deployment on gce with k8s


To update this file

1. Clone it to your local machine
2. Create a new branch
3. Make edits to the dockerfiles in the `worker` and `notebook` directories.  
4. Commit your changes
5. Tag your image with `python bump.py`
6. Push to github and make a pull request to master
7. If your build passes on Travis, we'll merge it and it will deploy to dockerhub 

Any questions please email jsimcock@rhg.com
