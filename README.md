# Python Developer Test Assignment - Paxful

The documentation included in this repository describe how to use the **Paxful API**.
The API was created using **Python 3** standalone mode and **MySQL 8.0.17** as database. This project uses macOS Mojave as the environment recommended to run, test and validate.

**NOTE:** THIS PROJECT IS NOT READY TO PRODUCTION ENVIRONMENT

## Setup - Local Environment

As mentioned above this project was created, developed, and tested on macOS Mojave if you are in another operational system, please in the case of errors will be necessary adjust some steps to your needs.

### Requirements

* macOs Mojave
* Mysql Installed (into a Docker container)
* Python 3 Installed (into the host machine)

### MySQL

The MySQL 8.0.17 was selected because is the more light, flexible, and scalable in the cloud. In this project was used only official docker images from the projects owners.

Download the official **MySQL 8.0.17** docker image defined with the tag as **latest**:

```
$ docker pull mysql
```

Create a directory to store the MySQL data in persistent mode, avoiding loss data in the reboot, stop or any error with the container itself:

```
$ mkdir /tmp/datadir
```

Run the MySQL, using the directory path to persistent data, defining the root password to the database, and exposing the port of database in the local network:

```
$ docker run --name standalone-mysql -p 3306:3306 -h localhost -e MYSQL_ROOT_PASSWORD=password -v /tmp/datadir:/var/lib/mysql -d mysql:latest
```

Restoring the Entity Relational Model from the SQL file [paxful_api_er.sql](./paxful_api_er.sql):

```
$ docker exec -i standalone-mysql sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' < paxful_api_er.sql
```

### API

The API will run on the HOST. For the production environment will be necessary to adjust the container of Mysql to expose an address into a private domain to allow the application to reach this address.

Install the lightning-fast ASGI server:

```
$ pip3 install uvicorn
```

To run the API will be necessary to stay inside of **app/** path:

```
$ cd paxful/app

$ /Library/Frameworks/Python.framework/Versions/3.7/bin/uvicorn main:app --reload
```

The API will be available to use and validate on http://127.0.0.1:8000 

To use the better resources of FASTAPI please access: http://localhost:8000/docs(recommended to test on a browser) OR http://localhost:8000/redoc

The documentation its included into the links mentioned above.

### Hardcode Authentication

To use the endpoint **/v1/statistics/** will be necessary use the hardcoded token **85d9b183-d1b6-11e9-aae0-0242ac110002-19c663b4-d26c-11e9-aae0-0242ac110002**.

### TODO LIST

* Create two custom containers to run on Kubernetes - Mysql and API.
* Will be nice refactoring some pieces of the code to reduce some similar behaviors with a properly classes.
* Add CI/CD to have better visibility regarding the flow of development.
* Creates the unittests to automate the checklist of requirements and coverage of the code.
* Create the second-factor authentication.
* Check the performance of the solution.
