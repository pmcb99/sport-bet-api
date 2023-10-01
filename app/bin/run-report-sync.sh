#!/bin/sh
cd app
export PYTHONPATH=$(pwd)
doppler run -- pipenv run python server/report/sync_reports.py

