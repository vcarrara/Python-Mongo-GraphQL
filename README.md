# Python-Mongo-GraphQL

GraphQL API built with Python. The API queries a distant MongoDB database. The program can be run inside a Docker container.

## Requirements

- Docker

## Local development

Start the service

```
$ docker-compose build
$ docker-compose up [-d]
```

Stop the service

```
$ docker-compose down
```

## Production deployment

## Environment variables

| Variable              | Description                                                                   | Valeur par défault                                                           |
| --------              | -----------------------------------                                           | ------------------                                                           |
| PORT                  | GraphQL API port                                                              | 80                                                                           |
| API_ENDPOINT          | GraphQL API endpoint                                                          | /                                                                            |
| DB_ENDPOINT           | MongoDB endpoint                                                              | python-mongo-graphql.37e9n.mongodb.net/social?retryWrites=true&w=majority    |
| DB_USER               | MongoDB username                                                              | user                                                                         |
| DB_PASSWORD           | MongoDB password                                                              | user                                                                         |
| USE_DATALOADER        | Wheter the API should use a dataloader to retrieve information (perf. gain)   | true                                                                         |
| COMPANIES_PER_PAGE    | Number of companies returned when a *page* param is provided                  | 2                                                                            |
| POSTS_PER_PAGE        | Number of posts per company returned when a *page* param is provided          | 2                                                                            |
| INTERACTIONS_PER_PAGE | Number of interactions per post returned when a *page* param is provided      | 2                                                                            |