# FYP-Prototype

Prototype version for my Final Year Project. This is the source code to run a vector database on a server and epxpose a new API built using python to interact and query the database.

## Project Deployment

## Setup SSH Tunnel to Connect from Outside Eduroam

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

## Running the Server

The server can be built locally or on the UCL CS virtual machine `hstanway-fyp` at `hstanway-fyp.cs.ucl.ac.uk`. These commands will automatically start and stop the server within Docker. Therefore, Docker must be installed on your machine before you can run the project. Additionally, there is no need to install any of the project's dependencies manually as this will be done automatically by docker.

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

## Developer Tools

Finally, if any modifications are made directly to the source code, use the following commands to run a formatter on all project files:

```[makefile]
make install-dev-tools
make black
make isort
```
