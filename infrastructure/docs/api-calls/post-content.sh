#!/bin/bash
set -ae

REST_ENDPOINT="https://zzaadhongd.execute-api.eu-west-1.amazonaws.com/prod"

curl -X POST $REST_ENDPOINT/note \
   -H 'Content-Type: application/json' \
   -H 'Accept: application/json' \
  -d @./sample-note.json