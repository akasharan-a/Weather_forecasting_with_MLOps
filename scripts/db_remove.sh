#!/bin/sh

# Start Docker service
echo "Removing DBs..."
sudo docker rm influxdb
docker volume rm -f $(docker volume ls -q)
echo "--Done--"
