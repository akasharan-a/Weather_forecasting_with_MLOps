#!/bin/sh

# Stop Docker service
echo "Stopping Docker service..."
sudo docker stop $(sudo docker ps -q)
sudo systemctl stop docker
echo "--Done--"
