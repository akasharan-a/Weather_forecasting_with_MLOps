#!/bin/sh

# Start Docker service
echo "Starting  DB..."
sudo systemctl start docker
docker compose up influxdb
echo "--Done--"
