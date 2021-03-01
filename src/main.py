from flask import Flask
from flask_graphql import GraphQLView
import logging
import logging.config
import os
from schema import schema


app = Flask(__name__)

PORT = int(os.getenv('PORT', 80))
ENDPOINT = os.getenv('API_ENDPOINT', '/graphql')

app.add_url_rule(ENDPOINT, view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True
))


if __name__ == '__main__':
    app.run(debug=True, port=PORT, host="0.0.0.0")
