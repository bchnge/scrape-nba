#!/bin/bash

session_name="scrape_nba"
package_env_name="py38"

tmux new -ds $session_name
echo $package_env_name
tmux send-keys -t $session_name "conda activate $package_env_name" C-m
tmux send-keys -t $session_name 'python scrape.py' C-m
