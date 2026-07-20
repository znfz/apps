#!/bin/bash

# Source the Conda setup script
source /data/miniconda3/etc/profile.d/conda.sh

# Activate the Conda environment
conda activate chatbot

# Run the Streamlit app
streamlit run app.py