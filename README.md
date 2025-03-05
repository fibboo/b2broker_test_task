# Project: b2broker_test_task

## Description
This project is a test task built with Django DRF. API documentation is available in Swagger format at the URL provided below.

## Quick Start

Follow these steps to quickly set up and run the project:

1. **Clone the repository**:
   ```bash
   git clone git@github.com:fibboo/b2broker_test_task.git
   ```

2. **Navigate to the repository folder**:
   ```bash
   cd b2broker_test_task
   ```

3. **Build the Docker images**:
   ```bash
   docker compose build
   ```

4. **Start the project**:
   ```bash
   docker compose up
   ```

Once all steps are completed, your project will be available at:  
[http://localhost:8000](http://localhost:8000)

---

## API Documentation

The project provides built-in API documentation, available via Swagger or Redoc. To access it, open the following URL after starting the project:

[http://localhost:8000/api/docs/swagger/](http://localhost:8000/api/docs/swagger/)

[http://localhost:8000/api/docs/redoc/](http://localhost:8000/api/docs/redoc/)

---

## Running Tests

You can verify the functionality of the project by running the tests. There are two ways to do so:

1. **Inside the Docker container**:
   ```bash
   docker compose exec backend python manage.py test
   ```

2. **Locally (if you have Python installed)**:
   Ensure your virtual environment is activated, then run:
   ```bash
   python manage.py test
   ```

---
