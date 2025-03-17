#!/bin/sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ENV_FILE=$SCRIPT_DIR/../.env

# Set the environment variables
load_env() {
    if [ -f $ENV_FILE ]; then
        for line in $(cat $ENV_FILE); do
            export $line
            echo "Setting $line"
        done
    else
        echo "No .env file found"
    fi
}

load_py_path() {
    echo "Update PATH"
    main_dir="$SCRIPT_DIR/app"
    export PYTHONPATH=$PYTHONPATH:$main_dir
}

# Run the command with the environment variables
run_with_env() {
    load_env
    load_py_path
    $@
}

run_with_env $@
