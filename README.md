# ![Docker-LAMP][logo]
Docker-LAMP-CGI is a fork of [Docker-LAMP](https://github.com/mattrayner/docker-lamp) by Matt Rayner. It is a docker image that include the phusion baseimage (20.04 variety), along with a LAMP stack ([Apache][apache], [MySQL][mysql] and [PHP][php]) all in one handy package. Compared to the upstream version, Docker-LAMP-CGI adds support to CGI scripts.

[![Build Status][shield-build-status]][info-build-status]
[![Docker Hub][shield-docker-hub]][info-docker-hub]
[![License][shield-license]][info-license]

## Image Versions

| Component                | `latest` |
| :--:                     |  :--:    |
| [Apache][apache]         | `2.4.41` |
| [MySQL][mysql]           | `8.0.26` |
| [PHP][php]               | `8.0.10` |
| [phpMyAdmin][phpmyadmin] | `5.1.1`  |


## Using the image
### On the command line
This is the quickest way
```bash
# Launch a 20.04 based image with PHP 8
docker run -p "80:80" -v ${PWD}/app:/app gdsyzxzcx/lampcgi:latest
```

### With a Dockerfile
```docker
FROM gdsyzxzcx/lampcgi:latest

# Your custom commands

CMD ["/run.sh"]
```

### MySQL Databases
By default, the image comes with a `root` MySQL account that has no password. This account is only available locally, i.e. within your application. It is not available from outside your docker image or through phpMyAdmin.

When you first run the image you'll see a message showing your `admin` user's password. This user can be used locally and externally, either by connecting to your MySQL port (default 3306) and using a tool like MySQL Workbench or Sequel Pro, or through phpMyAdmin.

If you need this login later, you can run `docker logs CONTAINER_ID` and you should see it at the top of the log.

#### Creating a database
So your application needs a database - you have two options...

1. PHPMyAdmin
2. Command line

##### PHPMyAdmin
Docker-LAMP comes pre-installed with phpMyAdmin available from `http://DOCKER_ADDRESS/phpmyadmin`.

**NOTE:** you cannot use the `root` user with PHPMyAdmin. We recommend logging in with the admin user mentioned in the introduction to this section.

##### Command Line
First, get the ID of your running container with `docker ps`, then run the below command replacing `CONTAINER_ID` and `DATABASE_NAME` with your required values:
```bash
docker exec CONTAINER_ID  mysql -uroot -e "create database DATABASE_NAME"
```


## Adding your own content
The 'easiest' way to add your own content to the lamp image is using Docker volumes. This will effectively 'sync' a particular folder on your machine with that on the docker container.

The below examples assume the following project layout and that you are running the commands from the 'project root'.
```
/ (project root)
/app/ (your PHP files live here)
/mysql/ (docker will create this and store your MySQL data here)
```

In english, your project should contain a folder called `app` containing all of your app's code. That's pretty much it.

### Adding your app
The below command will run the docker image `gdsyzxzcx/lampcgi:latest` interactively, exposing port `80` on the host machine with port `80` on the docker container. It will then create a volume linking the `app/` directory within your project to the `/app` directory on the container. This is where Apache is expecting your PHP to live.
```bash
docker run -i -t -p "80:80" -v ${PWD}/app:/app gdsyzxzcx/lampcgi:latest
```

### Persisting your MySQL
The below command will run the docker image `gdsyzxzcx/lampcgi:latest`, creating a `mysql/` folder within your project. This folder will be linked to `/var/lib/mysql` where all of the MySQL files from container lives. You will now be able to stop/start the container and keep your database changes.

You may also add `-p 3306:3306` after `-p 80:80` to expose the mysql sockets on your host machine. This will allow you to connect an external application such as SequelPro or MySQL Workbench.
```bash
docker run -i -t -p "80:80" -v ${PWD}/mysql:/var/lib/mysql gdsyzxzcx/lampcgi:latest
```

### Doing both
The below command is our 'recommended' solution. It both adds your own PHP and persists database files. We have created a more advanced alias in our `.bash_profile` files to enable the short commands `ldi` and `launchdocker`. See the next section for an example.
```bash
docker run -i -t -p "80:80" -v ${PWD}/app:/app -v ${PWD}/mysql:/var/lib/mysql gdsyzxzcx/lampcgi:latest
```

#### `.bash_profile` alias examples
The below example can be added to your `~/.bash_profile` file to add the alias commands `ldi` and `launchdocker`. 
```bash
# A helper function to launch docker container using gdsyzxzcx/lampcgi with overrideable parameters
#
# $1 - Apache Port (optional)
# $2 - MySQL Port (optional - no value will cause MySQL not to be mapped)
function launchdockerwithparams {
    APACHE_PORT=80
    MYSQL_PORT_COMMAND=""
    
    if ! [[ -z "$1" ]]; then
        APACHE_PORT=$1
    fi
    
    if ! [[ -z "$2" ]]; then
        MYSQL_PORT_COMMAND="-p \"$2:3306\""
    fi

    docker run -i -t -p "$APACHE_PORT:80" $MYSQL_PORT_COMMAND -v ${PWD}/app:/app -v ${PWD}/mysql:/var/lib/mysql gdsyzxzcx/lampcgi:latest
}
alias launchdocker='launchdockerwithparams $1 $2'
alias ldi='launchdockerwithparams $1 $2'
```

##### Example usage
```bash
# Launch docker and map port 80 for apache
ldi

# Launch docker and map port 8080 for apache
ldi 8080

# Launch docker and map port 3000 for apache along with 3306 for MySQL
ldi 3000 3306
```


## Developing the image
### Building and running
```bash
# Clone the project from Github
git clone https://github.com/kad-ecoli/docker-lamp-cgi
cd docker-lamp-cgi

# Build the images
docker build --network=host -t=gdsyzxzcx/lampcgi:latest -f ./latest/Dockerfile .

# Run the image as a container
docker run -d -p "3000:80" gdsyzxzcx/lampcgi:latest

# Sleep to allow the container to boot
sleep 30

# check container ID
docker ps | grep gdsyzxzcx/lampcgi | cut -f1 -d' '

# check container IP, where ${docker_machine_ID} is the ID obtained above
docker inspect ${docker_machine_ID) |grep IPAddress

# Curl out the contents of our new container, where ${docker_machine_ip} is the IP address obtained above
curl "http://${docker_machine_ip}:3000/"
```

### Testing
We use `docker-compose` to setup, build and run our testing environment. It allows us to offload a large amount of the testing overhead to Docker, and to ensure that we always test our image in a consistent way that's not affected by the host machine.

### One-line testing command
We've developed a single-line test command you can run on your machine within the `docker-lamp` directory. This will test any changes that may have been made, as well as comparing installed versions of Apache, MySQL, PHP and phpMyAdmin against those expected.
```bash
docker-compose -f docker-compose.test.yml -p ci build; docker-compose -f docker-compose.test.yml -p ci up -d; cd tests && ./test.sh; echo "Exited with status code: $?";
```

So what does this command do?

#### `docker-compose -f docker-compose.test.yml -p ci build;`
First, build that latest version of our docker-compose images.

#### `docker-compose -f docker-compose.test.yml -p ci up -d;`
Launch our docker containers (`web2004-php8` etc.) in daemon mode.

#### `cd tests && ./test.sh;`
Change into the test directory and run out tests

#### `echo "Exited with status code: $?"`
Report back whether the tests passed or not


## License
Docker-LAMP-CGI is licensed under the [Apache 2.0 License][info-license].

[logo]: https://cdn.rawgit.com/mattrayner/docker-lamp/831976c022782e592b7e2758464b2a9efe3da042/docs/logo.svg

[apache]: http://www.apache.org/
[mysql]: https://www.mysql.com/
[php]: http://php.net/
[phpmyadmin]: https://www.phpmyadmin.net/

[end-of-life]: http://php.net/supported-versions.php

[info-build-status]: https://circleci.com/gh/mattrayner/docker-lamp
[info-docker-hub]: https://hub.docker.com/r/mattrayner/lamp
[info-license]: LICENSE

[shield-build-status]: https://img.shields.io/circleci/project/mattrayner/docker-lamp.svg
[shield-docker-hub]: https://img.shields.io/badge/docker%20hub-mattrayner%2Flamp-brightgreen.svg
[shield-license]: https://img.shields.io/badge/license-Apache%202.0-blue.svg

[dgraziotin-lamp]: https://github.com/dgraziotin/osx-docker-lamp
