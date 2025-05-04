# CleanTheWorld

## Running the application

### Initial setup

Before running the application, you need to setup Auth0 (a `Single Page Application` for the frontend and a `Machine to Machine` API for verifying the tokens in the backend).

Next, setup environment variables as described in the following files:

* frontend/src/env.js.example
* .env.example

### Running the application

Before running the application, as well as after any changes, you must build the docker image.

To build, run or stop the application, use standard docker compose commands:

* Build the image: `docker compose build`
* Run application in current terminal session: `docker compose up`
* Run application in the background: `docker compose up -d`
* Stop application running in the background: `docker compose down`
* Stop application and remove all volumes (this deletes all data in the database): `docker compose down --volumes`


### Using the system

By default, the app exposes the following ports:

* Port 80: Frontend
* Port 9090: API

Therefore when running the system locally, you can access:
* Frontend: http://127.0.0.1
* API docs: http://127.0.0.1:9090/docs
