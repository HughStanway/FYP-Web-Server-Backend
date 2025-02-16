# FYP-Prototype

Prototype version for my Final Year Project. This is the source code to run a vector database on a server and epxpose a new API built using python to interact and query the database.

## Start Server

Just run:

```[makefile]
make build
```

## Stop Server

To temporarily stop the server, run:

```[makefile]
make stop
```

To restart the server without stopping, run:

```[makefile]
make restart
```

To stop and remove everything (containers, networks, and volumes), run:

```[makefile]
make down
```

## Developing

After making changes to the API code (src/) reload the containers to apply new changes with:

```[makefile]
make reload
```

If the dependencies change you must instead run:

```[makefile]
make rebuild
```

Print server logs:

```[makefile]
make logs
```
