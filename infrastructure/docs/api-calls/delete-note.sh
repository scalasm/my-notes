#!/bin/bash
set -ae

NOTE_ID=${1}

REST_ENDPOINT="https://zzaadhongd.execute-api.eu-west-1.amazonaws.com/prod"

curl -X DELETE $REST_ENDPOINT/note/${NOTE_ID}