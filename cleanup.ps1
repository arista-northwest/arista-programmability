# delete ALL docker images, be CAREFUL
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
del *.o
