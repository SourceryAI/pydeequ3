#!/bin/sh

set -e -x

PARALLEL=$1


# Run coverage report
BASE_FOLDER="."
COVERAGE_HTML="--cov-report html:${BASE_FOLDER}/cov_html"
COVERAGE_XML="--cov-report xml:${BASE_FOLDER}/cov.xml"
COVERAGE_ANNOTATE="--cov-report annotate:${BASE_FOLDER}/cov_annotate"
COVERAGE_TERM="--cov-report term-missing"
COVERAGE_REPORT_CONF="${COVERAGE_HTML} ${COVERAGE_XML} ${COVERAGE_TERM}"
CODE_COVERAGE="${COVERAGE_REPORT_CONF} --cov=${BASE_FOLDER}"

# Speed up tests via test run parallelization
NUMCPUS=2
RETRY_CONF="--reruns 2 --reruns-delay 5 --looponfail"
PARALLEL_CONF="-n ${NUMCPUS} ${RETRY_CONF} --tx ${NUMCPUS}*popen//python=python"


if [ "$PARALLEL" == "true" ] || [ "$PARALLEL" == "yes" ]
then
  PYTEST_COMMAND="pytest ${PARALLEL_CONF} ${CODE_COVERAGE}"
elif [ -z ${PARALLEL} ]
then
  PYTEST_COMMAND="pytest ${CODE_COVERAGE}"
else
    echo "Invalid parallel $PARALLEL option, should be either true or yes, exiting with code 1"
    sleep 1
    exit 1
fi

echo "pytest command: ${PYTEST_COMMAND}"
poetry run $PYTEST_COMMAND
