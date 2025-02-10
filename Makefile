# Phony targets
.PHONY: help dev build start lint test prettier docker-dev docker-build docker-up docker-down

.EXPORT_ALL_VARIABLES:

PROJECT_SLUG := "chatbot"
APP_NAME := $(PROJECT_SLUG)
DOCKER_HUB := beafdocker

# Help target
help:
	@echo "Available commands:"
	@echo "  make dev         - Run the development server"
	@echo "  make build       - Build the production application"
	@echo "  make start       - Start the production server"
	@echo "  make lint        - Run linter"
	@echo "  make test        - Run e2e tests"
	@echo "  make prettier    - Run prettier"
	@echo "  make docker-dev  - Run the development server in Docker"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up   - Start Docker containers"
	@echo "  make docker-down - Stop Docker containers"

# ANSI color codes
GREEN=$(shell tput -Txterm setaf 2)
YELLOW=$(shell tput -Txterm setaf 3)
RED=$(shell tput -Txterm setaf 1)
BLUE=$(shell tput -Txterm setaf 6)
RESET=$(shell tput -Txterm sgr0)

## Docker
startTest:
	@echo "$(YELLOW)Starting docker environment...$(RESET)"
	docker compose -p $(PROJECT_SLUG) up --build

updateTest:
	docker compose -p $(PROJECT_SLUG) up --build -d

stopTest:
	@COMPOSE_PROJECT_NAME=$(PROJECT_SLUG) docker compose down


# Utilities
lint: ## Format project
	@echo "$(YELLOW)Running linters...$(RESET)"
	./scripts/lint.sh

test: ## Run backend tests
	@echo "$(YELLOW)Running tests...$(RESET)"
	./scripts/test.sh


dev: ## Serve the project in terminal
	fastapi dev app/main.py --host 0.0.0.0 --reload


sync: ## Sync dependencies
	uv sync && source .venv/bin/activate


# Deployment
deploy:
	@echo "$(YELLOW)Deploying to Vercel...$(RESET)"
	vercel deploy --prod


# Helpers
scaffold: ## Scaffold a resource
	@cd scripts && python scaffold.py run -n $(name)

pre-commit:
	npx concurrently --kill-others-on-fail --prefix "[{name}]" --names "lint,test" \
	--prefix-colors "bgRed.bold.white,bgGreen.bold.white,bgBlue.bold.white,bgMagenta.bold.white" \
	"./scripts/lint.sh" \
	"./scripts/test.sh"

pre-commit-docker:
	npx concurrently --kill-others-on-fail --prefix "[{name}]" --names "lint,test" \
	--prefix-colors "bgRed.bold.white,bgGreen.bold.white,bgBlue.bold.white,bgMagenta.bold.white" \
	"docker exec chatbot-1 ./scripts/lint.sh" \
	"docker exec chatbot-1 ./scripts/test.sh" 
