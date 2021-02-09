from flask import Flask
from flask_graphql import GraphQLView
import os


app = Flask(__name__)

app.add_url_rule(os.getenv('API_ENDPOINT', '/'), view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True
))

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT', 80), host="0.0.0.0")
