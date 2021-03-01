# Python-Mongo-GraphQL

GraphQL API built with Python. The API queries a distant MongoDB database. The program can be run inside a Docker container.

## Requirements

- Docker

## Local development

:rocket: Start the service

```
$ docker-compose -f docker-compose-monitoring.yml up [-d]
$ docker-compose up --build [-d]
```

Stop the service

```
$ docker-compose -f docker-compose-monitoring.yml down
$ docker-compose down
```

## Production deployment

## Environment variables

| Variable              | Description                                                                   | Valeur par défault                                                           |
| --------              | -----------------------------------                                           | ------------------                                                           |
| PORT                  | API port                                                                      | 80                                                                           |
| LOKI_IP               | IP of Loki                                                                    | null                                                                         |
| LOGS_PATH             | Path of gunicorn HTTP logs                                                    | logs/gunicorn.log                                                            |
| API_ENDPOINT          | GraphQL API endpoint                                                          | /graphql                                                                     |
| DB_ENDPOINT           | MongoDB endpoint                                                              | python-mongo-graphql.37e9n.mongodb.net/social?retryWrites=true&w=majority    |
| DB_PROTOCOL           | Protocol that should be used to connect MongoDB                               | mongodb+srv                                                                  |
| DB_USER               | MongoDB username                                                              | user                                                                         |
| DB_PASSWORD           | MongoDB password                                                              | user                                                                         |
| USE_DATALOADER        | Wheter the API should use a dataloader to retrieve information (perf. gain)   | true                                                                         |