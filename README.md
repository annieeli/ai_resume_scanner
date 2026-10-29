# AI Resume Analyzer: Distributed Processing Platform

An asynchronous, event-driven microservices platform that analyzes PDF resumes using LLMs. It highlights missing skills and analyzes resume and job posting compatability. Built to handle high-volume document ingestion without blocking the main API thread, mimicking enterprise-scale data pipelines.

## 🏗 System Architecture

> **Note:** Insert a visual architecture diagram here (a PNG of the flowchart we discussed earlier).

The platform is decoupled into three primary services to ensure fault tolerance and scalability:

1. **API Gateway (C#/.NET):** The synchronous entry point. Handles client uploads, validates payloads, saves raw binaries to blob storage, and publishes processing events to the message queue.
2. **Message Broker (RabbitMQ):** Orchestrates the asynchronous workload, ensuring no uploaded resumes are lost during traffic spikes or worker node failures.
3. **AI Worker Service (Python):** An independent background process that consumes messages from the queue, extracts PDF text, interfaces with the LLM API, and persists the structured analysis to the database.

## 🚀 Tech Stack

*   **Backend:** C# (API Gateway), Python (Worker)
*   **Infrastructure:** Docker, Docker Compose
*   **Database & Messaging:** PostgreSQL, RabbitMQ/AWS SQS
*   **AI/External APIs:** OpenAI API, PyPDF2
*   **Frontend:** React / Vanilla JS

## ⚙️ Local Setup & Quick Start

This project uses a monorepo structure and Docker Compose for zero-friction setup. 

**Prerequisites:**
* Docker and Docker Compose installed
* An OpenAI API Key

**Steps:**
1. Clone the repository:
   ```bash
   git clone [https://github.com/annieeli/resume-scanner-platform.git](https://github.com/annieeli/resume-scanner-platform.git)
   cd resume-scanner-platform