[![Docker badge](http://docker0.serv.pw:8080/danceos/dosek-base)](https://registry.hub.docker.com/u/danceos/dosek-base/)

We provide a [docker.io](http://www.docker.com) images for a basic
build environment. These images provide an SSH port and access to an
Ubuntu machine that contains all build dependencies. You can either
build the images yourself with

    cd scripts/docker; make
    make run
    make ssh

or you can pull it directly from the docker Hub

    docker pull danceos/dosek-base
    cd scripts/docker; make run; make ssh

In either cases, the password is `dosek`. In the default
configuration, no SSH port will be exposed to the outside world.

Please have a look at the source code repository for more information.

https://github.com/danceos/dosek
