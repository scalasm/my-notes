#!/bin/bash
set -ae

NOTE_ID=${1}

REST_ENDPOINT="https://zzaadhongd.execute-api.eu-west-1.amazonaws.com/prod"

curl -X GET $REST_ENDPOINT/note/${NOTE_ID} \
   -H 'Accept: application/json' \
