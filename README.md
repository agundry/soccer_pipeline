# Soccer Pipeline

This is a pipeline used for aggregating public twitter data, created for the US Soccer hackathon.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

```
Python 2.7
docker-compose
mysql
```

### Installing

A step by step series of examples that tell you how to get a development env running

Spin up docker containers

```
docker-compose up -d
```

Run flyway migrations

```
flyway migrate
```

Set up config file and replace with proper credentials

```
cp config.example.yaml config.yaml
```

