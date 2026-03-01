#!/bin/bash

# Script to manage Hazelcast nodes and logging service instances dynamically

if [ "$1" == "scale" ]; then
    if [ -z "$2" ] || [ -z "$3" ]; then
        echo "Usage: $0 scale <hazelcast_num> <logging_num>"
        exit 1
    fi
    docker compose up --scale hazelcast=$2 --scale logging=$3 -d
    echo "Scaled Hazelcast to $2 instances and logging to $3 instances"

elif [ "$1" == "stop_hazelcast" ]; then
    docker compose stop hazelcast
    echo "Stopped all Hazelcast nodes"

elif [ "$1" == "start_hazelcast" ]; then
    docker compose start hazelcast
    echo "Started Hazelcast nodes"

elif [ "$1" == "stop_logging" ]; then
    docker compose stop logging
    echo "Stopped all logging instances"

elif [ "$1" == "start_logging" ]; then
    docker compose start logging
    echo "Started logging instances"

elif [ "$1" == "stop_container" ]; then
    if [ -z "$2" ] || [ -z "$3" ]; then
        echo "Usage: $0 stop_container <service> <index>"
        echo "Example: $0 stop_container hazelcast 1"
        exit 1
    fi
    container_name="microservices-${2}-${3}"
    docker stop $container_name
    echo "Stopped container $container_name"

elif [ "$1" == "start_container" ]; then
    if [ -z "$2" ] || [ -z "$3" ]; then
        echo "Usage: $0 start_container <service> <index>"
        echo "Example: $0 start_container hazelcast 1"
        exit 1
    fi
    container_name="microservices-${2}-${3}"
    docker start $container_name
    echo "Started container $container_name"

elif [ "$1" == "status" ]; then
    docker compose ps

else
    echo "Usage: $0 {scale <hazelcast_num> <logging_num>|stop_hazelcast|start_hazelcast|stop_logging|start_logging|stop_container <service> <index>|start_container <service> <index>|status}"
fi