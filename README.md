# FastAPI-Base-Source 🚀

**Authored by:** NDK2509  
**Architecture:** Clean Architecture

---

## 🧩 What is this?

FastAPI-Base-Source is a boilerplate / base template built using FastAPI (Python) following a Clean Architecture
approach.  
It’s designed to give you a well-structured starting point for building web APIs with FastAPI — including Docker
support, tests, and a standard project layout.

---

## ✅ Key Features

- Clean Architecture structure (separating layers for domain, application, interface, infrastructure)
- Ready for production usage with Docker and docker-compose support
- Tests folder present for adding automated tests
- Pre-configured requirements for dependencies (`requirements.txt` and `requirements.test.txt`)
- Easy to extend and adapt for your own API project

---

## 🛠 Getting Started

### Prerequisites

- Python (3.8+)
- Docker & Docker Compose (for containerised development / production)
- Git (to clone the repo)

### Installation

```bash
git clone https://github.com/NDK2509/FastAPI-Base-Source.git  
cd FastAPI-Base-Source  
# (optional) Create and activate virtualenv  
python3 -m venv venv  
source venv/bin/activate  
# Install dependencies  
pip install -r requirements.txt  

