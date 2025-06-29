# Qwen Agentic Server

## Overview

This is the server component for my Qwen Agentic AI system.

This provides the inference loop and tools for the Qwen Agentic CLI (cli client), Qwen Agentic UX (web client), and the PICARD project.

> **Although initially designed with the Qwen models and Alibaba Cloud Model Studio in mind, this is compatible with almost any model and LLM endpoint (OpenAI compatible).**

## How to setup and run

```bash
#Clone
git clone https://github.com/jvroig/qwen-agentic-server.git

#Run setup script
cd qwen-agentic-server
python3 setup.py

#Run start.sh
bash start.sh
```

The setup script will generate the correct `start.sh` script for your system.

`start.sh` will create and activate virtual env as needed, install requirements, and then run the server.

## Configuration

Copy `.env.sample` into a new file called `.env` and replace with actual values for your setup.



## Tools Available
See [TOOLS.md](TOOLS.md) for the list of tools available in Qwen Agentic Server
