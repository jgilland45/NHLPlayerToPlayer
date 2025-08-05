# Makefile for NHL Player-to-Player Project
#
# This file provides convenient shortcuts for common development tasks,
# especially for managing the Dockerized Neo4j database and running the data pipeline.
#
# Usage:
#   make db-up       - Create and start a new Neo4j container for the first time.
#   make db-start    - Start the existing, stopped container.
#   make db-stop     - Stop the running container.
#   make db-restart  - Restart the container.
#   make db-down     - Stop and REMOVE the container.
#   make db-logs     - View the live logs from the container.
#   make db-status   - Check the status of all Docker containers.
#   make db-clear    - Wipe all data from the Neo4j database.
#   make db-populate - Run the Python script to populate the database.
#   make db-reset    - Wipe and then repopulate the database.
#

# Load environment variables from .env file if it exists.
# This allows us to use variables like NEO4J_PASSWORD in this file.
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# ==============================================================================
# Docker & Database Management
# ==============================================================================

.PHONY: db-up db-start db-stop db-restart db-down db-logs db-status

db-up:
	@echo "Starting new Neo4j container 'nhl-graph-db'..."
	@docker run \
		--name nhl-graph-db \
		-p 7474:7474 -p 7687:7687 \
		-v $(shell pwd)/neo4j-data:/data \
		-d \
		-e NEO4J_AUTH=neo4j/$(NEO4J_PASSWORD) \
		neo4j:latest

db-start:
	@echo "Starting existing Neo4j container..."
	@docker start nhl-graph-db

db-stop:
	@echo "Stopping Neo4j container..."
	@docker stop nhl-graph-db

db-restart:
	@echo "Restarting Neo4j container..."
	@docker restart nhl-graph-db

db-down:
	@echo "Stopping and removing Neo4j container..."
	@docker stop nhl-graph-db || true
	@docker rm nhl-graph-db || true

db-logs:
	@docker logs -f nhl-graph-db

db-status:
	@docker ps -a

# ==============================================================================
# Data Pipeline Management
# ==============================================================================

.PHONY: db-clear db-populate db-reset

export PYTHONPATH=$(shell pwd)

db-clear:
	@echo "Clearing all data from the database..."
	@python3 backend/data_pipeline/run_pipeline.py --clear

db-get-remaining-years:
	@echo "Getting years to still process..."
	@python3 backend/data_pipeline/run_pipeline.py --years-remaining

db-populate:
	@echo "Running the data pipeline to populate the database..."
	@python3 backend/data_pipeline/run_pipeline.py

db-reset: db-clear db-populate
