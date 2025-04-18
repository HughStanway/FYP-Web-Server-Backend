# FYP-Prototype

This is the source code for a proof-of-concept Code Similarity Search based web server. It provides an API that can be queired over HTTP to create, initialise and search from collections of code snippets

## 1. Project Deployment

A demo version of this project is deployed on a UCL VM at `hstanway-fyp.cs.ucl.ac.uk`. The server should already be running on this machine thus requests can be made to the API using the servers URL (Please note that as this is a UCL VM it can only be accessed from within the Eduroam network. If you are using the server from outside this network please follow the steps described in section '2. Setup SSH Tunnel to Connect from Outside Eduroam'). 

Additionally, the server can be accessed remotly over SSH. This allows you to start/stop the project and view a live feed of the servers logs. In order to SSH into the VM, please first SSH into `tails.cs.ucl.ac.uk` or `knuckles.cs.ucl.ac.uk` then SSH into `hstanway-fyp.cs.ucl.ac.uk` (Please note you may need have your UCL CS account authorized to access the VM by the department before you can do this). Finally, once you have connected, run `cd /home/hstanway/FYP-Prototype/` to access the correct directory and then use the commands listed in the section '3. Running the Server' to interact with the server.

Finally, the API supports the following requests:

### Create

Used to create a new collection.

```[bash]
curl -X POST http://localhost/create -H "Content-Type: application/json" -d '{"collectionName": "NewCollection"}'
```

### Insert

Used to insert method from a Git repository into a collection.

```
curl -X POST http://localhost/insert -H "Content-Type: application/json" -d '{"collectionName": "NewCollection", "repositories":[{"repoName":"simple-java-methods.git", "commitHash":"081ce30276353e017f11a9c556427205bfa38124"}]}'
```

### Query

Make code search queries to a collection.

```
curl -X POST http://localhost/query -H "Content-Type: application/json" -d '{"collectionName": "Apache", "payload":"Find the Maximum Integer in an array"}'
```

## 2. Setup SSH Tunnel to Connect from Outside Eduroam

The web server API can only be accessed within Eduroams firewall. Therefore, you will need to setup an SSH tunnel in order to interact to the server from outside Eduroam. Without this any requests made to `hstanway-fyp.cs.ucl.ac.uk` will be blocked.

This can be setup by first adding the following to the `.ssh/config` file on your local machine:

```[bash]
host knuckles
   HostName knuckles.cs.ucl.ac.uk
   User [Your User Name]

host fyp
   HostName hstanway-fyp.cs.ucl.ac.uk
   User [Your User Name]
   ProxyJump knuckles
```

Once you have done this, you can open a tunnel on your machines `localhost` that will forward requests to the web server using the following command:

```[bash]
ssh -L 8888:localhost:80 fyp
```

Now any requests made to `localhost:8888` will be forwarded to `fyp:80` via knuckles. Therefore, instead of makeing API requests to `hstanway-fyp.cs.ucl.ac.uk` you should now make them to `localhost:8888`. 

Finally, once you close the SSH session the tunnel will close and thus the requets will no longer work.

## 3. Running the Server

The server can be built locally using `localhost` or on the UCL CS virtual machine `hstanway-fyp` at `hstanway-fyp.cs.ucl.ac.uk`. These commands will automatically start and stop the server within Docker. Therefore, Docker must be installed on your machine before you can run the project. Additionally, there is no need to install any of the project's dependencies manually as this will be done automatically by docker.

### Start Server

To start the server, just run:

```[makefile]
make build
```

### Stop Server

To stop the server and remove all containers, run:

```[makefile]
make down
```

This will stop the server but keep all saved volumes (e.g. it will not delete the database). However, if you want to stop and remove everything (including deleting the vector database), run:

```[makefile]
make prune
```

To view the server logs, run:

```[makefile]
make logs
```

## 4. Developer Tools

Finally, if any modifications are made directly to the source code, use the following commands to run a formatter on all project files:

```[makefile]
make install-dev-tools
make black
make isort
```
