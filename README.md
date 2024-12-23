# Coding Assignment Auto-Review Tool

The **Coding Assignment Auto-Review Tool** is a scalable, automated code review system that integrates GitHub, Redis, and Groq AI APIs to deliver structured, actionable feedback on coding assignments. Designed for technical teams, the tool retrieves code from GitHub repositories, analyzes it using AI, and provides detailed reviews tailored to the developer's skill level and assignment requirements.

<!-- TOC -->
* [What If](#what-if)
  * [Handling Large Repositories](#1-handling-large-repositories)
  * [Handling High Traffic (100+ Requests/Minute)](#2-handling-high-traffic-100-requestsminute)
  * [Managing OpenAI and GitHub API Usage](#3-managing-openai-and-github-api-usage)
  * [Database and Infrastructure](#4-database-and-infrastructure)
* [Features](#features)
* [Setup Instructions](#setup-instructions)
  * [Manual Setup](#manual-setup)
  * [Docker Setup](#docker-setup)
  * [Tests](#tests)
* [API Endpoints](#api-endpoints)
<!-- TOC -->

---

## What If

### 1. Handling Large Repositories
To process repositories with 100+ files efficiently, I would:
- Use **Redis** to cache file metadata and content for previously accessed repositories.
- Fetch files concurrently using asynchronous operations, minimizing network latency.
- Limit the depth and size of file analysis during the initial phase, focusing on files relevant to the assignment description.

### 2. Handling High Traffic (100+ Requests/Minute)
To scale the system for high traffic, I would:
- Deploy the service on a container orchestration platform like **Kubernetes** for auto-scaling.
- Use a **Load Balancer** (e.g., AWS ALB or NGINX) to distribute requests across multiple service instances.
- Integrate **Celery** with a distributed task queue like **RabbitMQ** to process code reviews asynchronously.
- Use **Redis** or a persistent database for managing job queues and user requests.

### 3. Managing OpenAI and GitHub API Usage
- Implement **rate-limit tracking** using Redis to prevent API throttling.
- Batch API calls for file content retrieval where possible.
- Explore alternative AI models (e.g., open-source models like Hugging Face) to reduce API dependency and cost.
- Monitor API usage using observability tools like **Prometheus** and **Grafana**, and implement retries for transient failures.

### 4. Database and Infrastructure
- Store persistent data like user requests, reviews, and repository metadata in a **PostgreSQL** database.
- Use **CloudFront** or similar CDN services to cache static responses for repeated queries.
- Host the service in a **cloud-native environment** (AWS, GCP, or Azure) with support for serverless functions or containerized microservices.

---

## Features

- **GitHub Integration**: Fetches files from GitHub repositories, supports nested directory structures, and caches responses.
- **Redis Caching**: Implements efficient rate-limit handling and file content caching to reduce redundant API calls.
- **AI-Powered Reviews**: Uses Groq AI APIs for generating structured code reviews based on the assignment description, candidate level, and provided code.
- **Scalable Architecture**: Designed to handle high traffic and large repositories.

---

## Setup Instructions

### Manual Setup

1. **Environment Variables**:
   - Set `GITHUB_API_TOKEN` for accessing GitHub repositories.
   - Set `GROQ_API_TOKEN` for accessing Groq AI API.
   - Configure Redis credentials as needed. 
   - You can find examples of environment in [.env.sample](.env.sample) file.

2. **Installation**:
   * Install the dependencies:
   ```bash
   poetry install
   ```
   * Activate the virtual environment created by poetry:
   ```bash
   poetry shell
   ```
   
3. **Run the Service**:
   Start the service using an ASGI server like `uvicorn`:
   ```bash
   uvicorn src.main:app
   ```
   
### Docker Setup
1. **Environment Variables**:
   - Set `GITHUB_API_TOKEN` for accessing GitHub repositories.
   - Set `GROQ_API_TOKEN` for accessing Groq AI API.
   - Configure Redis credentials as needed. 
   - You can find examples of environment in [.env.sample](.env.sample) file.

2. **Run the Docker**:
   ```bash
   docker-compose up --build
   ```

### Tests
To run tests you can just use:
```bash
pytest
```
Or full directory path:
```bash
pytest src/code_guru/tests
```

---

## API Endpoints

### POST `/review`
Submit a code review request with the following payload:
```json
{
  "github_repo_url": "https://github.com/username/repo-name",
  "assignment_description": "Implement an optimized sorting algorithm.",
  "candidate_level": "Junior"
}
```

Response:
```json
{
  "filenames": ["file1.py", "file2.py"],
  "review_result": "Detailed review with downsides, rating, and suggestions."
}
```
