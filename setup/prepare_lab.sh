#!/bin/bash

# Obtain the true location of this script
SCRIPT_TRUEPATH="$( readlink -f $0 )"

# Extract the path of this script from the true path
SCRIPT_BASEPATH="$( dirname ${SCRIPT_TRUEPATH} )"

# Where lab files should be copied
TARGET_DIRECTORY=~/abc-en

# Python interpreter
PYTHON_VENV=~/venv
PYTHON_BIN=${PYTHON_VENV}/bin/python
PYTHON_PIP_BIN=${PYTHON_VENV}/bin/pip

CML_STARTUP_SCRIPT=${SCRIPT_BASEPATH}/launch_topology.py

CMD="${PYTHON_BIN} ${CML_STARTUP_SCRIPT}"


LABS="git \
python-exceptions \
pyats-testbed \
snapshots \
pyats-cli \
pyats-jinja2 \
pyats-model \
restconf"
# pyats-restconf"

# Execute the setup tasks....
echo
echo "******************************************************************************"
echo "Beginning lab preparation tasks..."
echo "******************************************************************************"
echo

sudo apt-get install -y man

# This should be performed as the first step in the lab.
#echo "******************************************************************************"
#echo "Pulling latest content from remote repository..."
#echo "******************************************************************************"
#echo
#
#cd ${SCRIPT_BASEPATH}/..
#git pull

echo "******************************************************************************"
echo "Starting CML topology..."
echo "******************************************************************************"
echo

${CMD}

echo
echo "******************************************************************************"
echo "Copying lab activity files..."
echo "******************************************************************************"
echo

mkdir -p ${TARGET_DIRECTORY}

for LAB in ${LABS}; do
  LAB_PATH=${SCRIPT_BASEPATH}/../${LAB}/lab
  echo "Preparing activity ${LAB}..."
  if [ -d ${LAB_PATH} ]; then
    # mkdir -p ${TARGET_DIRECTORY}/${LAB}
    cp -prf ${LAB_PATH}/ ${TARGET_DIRECTORY}/${LAB}/
  else
    echo "No lab directory found - skipping..."
  fi
done

echo
echo "******************************************************************************"
echo "Lab preparation tasks complete!"
echo "******************************************************************************"
echo
