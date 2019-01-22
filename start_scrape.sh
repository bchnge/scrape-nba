#!/bin/bash

session_name="scrape_nba"

tmux new -ds $session_name
tmux send-keys -t $session_name 'python scrape.py' C-m
