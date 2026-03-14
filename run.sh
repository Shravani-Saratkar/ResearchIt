#!/usr/bin/env bash

echo "Starting ResearchIt on Render..."

streamlit run app.py --server.port $PORT --server.address 0.0.0.0