# Ironnect

Ironnect is a gateway to provide Large Language Models (LLMs) as a service.

It is a RESTful API that allows users to interact with LLMs in a simple and efficient way.

## Prerequisites

It's required to have the following installed on your machine:

- python >= 3.7
- pip

## Setup

To install the dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Run

Depending on the environment, you can run the application using the following commands:

### Development

Run the application using the following command with the debug mode enabled and auto-reload:

```bash
flask run --debug --reload
```

### Production

Run the application using the following command with the production server for better performance:

```bash
sh startup.sh
```
