from functools import reduce
from bson import ObjectId
import os
import pymongo

client = pymongo.MongoClient(
    f"{os.getenv('DB_PROTOCOL', 'mongodb+srv')}://{os.getenv('DB_USER', 'user')}:{os.getenv('DB_PASSWORD', 'user')}@{os.getenv('DB_ENDPOINT', 'python-mongo-graphql.37e9n.mongodb.net/social?retryWrites=true&w=majority')}")

db = client['social']
companies_collection = db['companies']
posts_collection = db['posts']
interactions_collection = db['interactions']
users_collection = db['users']


def retrieve_collections():
    return db.collection_names()


def retrieve_companies(_id, projection, page):
    aggregation = []
    if _id:
        aggregation.append({
            '$match': {'_id': ObjectId(_id)}
        })
    aggregation.append({
        '$project': projection
    })
    return list(companies_collection.aggregate(aggregation))


def retrieve_posts(company_id, source, projection, page):
    aggregation = []
    if company_id:
        aggregation.append({
            '$match': {'companyId': ObjectId(company_id)}
        })
    if source:
        aggregation.append({
            '$match': {'source': source}
        })
    aggregation.append({
        '$project': projection
    })
    return list(posts_collection.aggregate(aggregation))


def insert_post(args):
    return posts_collection.insert_one(args)


def insert_interaction(args):
    return interactions_collection.insert_one(args)


def update_company(company_id, update):
    return companies_collection.update_one({'_id': ObjectId(company_id)}, {'$set': update}, upsert=False)


def update_post(post_id, update):
    return posts_collection.update_one({'_id': ObjectId(post_id)}, {'$set': update}, upsert=False)


def update_interaction(interaction_id, update):
    return interactions_collection.update_one({'_id': ObjectId(interaction_id)}, {'$set': update}, upsert=False)


def retrieve_user(user_id, projection):
    aggregation = [
        {'$match': {'_id': ObjectId(user_id)}}
    ]
    if projection:
        aggregation.append({'$project': projection})
    return list(users_collection.aggregate(aggregation))[0]


def retrieve_users(ids):
    return list(users_collection.aggregate([
        {
            '$match': {'_id': {'$in': ids}}
        },
        {
            '$addFields': {'__order': {'$indexOfArray': [ids, "$_id"]}}
        },
        {
            '$sort': {'__order': 1}
        }
    ]))


def retrieve_interactions_from_post(post_id, projection, page):
    aggregation = [
        {
            '$match': {'postId': post_id}
        },
        {
            '$project': projection
        }
    ]
    return list(interactions_collection.aggregate(aggregation))


def retrieve_interactions_from_posts(postIds):
    interactions = list(interactions_collection.aggregate([
        {
            '$group': {
                '_id': '$postId',
                'interactions': {
                    '$push': '$$ROOT'
                }
            }
        }, {
            '$match': {
                '_id': {
                    '$in': postIds
                }
            }
        }, {
            '$addFields': {
                '__order': {
                    '$indexOfArray': [postIds, '$_id']
                }
            }
        }, {
            '$sort': {
                '__order': 1
            }
        }, {
            '$project': {
                '_id': 0,
                '__order': 0
            }
        }
    ]))
    return [interaction['interactions'] for interaction in interactions]


def retrieve_count_posts(_id, source):
    aggregation = []
    aggregation.extend(
        [
            {
                '$match': {'_id': ObjectId(_id)}
            }, {
                '$lookup': {
                    'from': 'posts',
                    'localField': '_id',
                    'foreignField': 'companyId',
                    'as': 'posts'
                }
            }, {
                '$unwind': {'path': '$posts'}
            }
        ]
    )
    if source:
        aggregation.append({
            '$match': {'posts.source': source}
        })
    aggregation.extend(
        [
            {
                '$group': {
                    '_id': ObjectId(_id),
                    'posts': {'$push': '$posts'}
                }
            }, {
                '$project': {
                    'number': {'$size': '$posts'}
                }
            }
        ]
    )
    return list(companies_collection.aggregate(aggregation))


def retrieve_interactions(_id, projection):
    aggregation = [
        {
            '$match': {
                'companyId': ObjectId(_id)
            }
        }, {
            '$lookup': {
                'from': 'interactions',
                'localField': '_id',
                'foreignField': 'postId',
                'as': 'interactions'
            }
        }, {
            '$unwind': {
                'path': '$interactions'
            }
        }, {
            '$group': {
                '_id': {
                    'companyId': '$companyId',
                    'source': '$source'
                },
                'likes': {
                    '$sum': '$interactions.likes'
                },
                'comments': {
                    '$sum': '$interactions.comments'
                },
                'shares': {
                    '$sum': '$interactions.shares'
                }
            }
        }, {
            '$project': projection
        }
    ]
    return list(posts_collection.aggregate(aggregation))


def retrieve_evolution(company_id, projection):
    aggregation = [
        {
            '$match': {
                'companyId': ObjectId(company_id)
            }
        }, {
            '$lookup': {
                'from': 'interactions',
                'localField': '_id',
                'foreignField': 'postId',
                'as': 'interactions'
            }
        }, {
            '$unwind': {
                'path': '$interactions'
            }
        }, {
            '$sort': {
                'interactions.date': -1
            }
        }, {
            '$addFields': {
                'week': {
                    '$isoWeek': {
                        '$toDate': '$date'
                    }
                },
                'year': {
                    '$isoWeekYear': {
                        '$toDate': '$date'
                    }
                }
            }
        }, {
            '$group': {
                '_id': {
                    '_id': '$_id',
                    'source': '$source'
                },
                'interaction': {
                    '$first': '$interactions'
                },
                'week': {
                    '$first': '$week'
                },
                'year': {
                    '$first': '$year'
                }
            }
        }, {
            '$group': {
                '_id': {
                    'week': '$week',
                    'year': '$year',
                    'source': '$_id.source'
                },
                'likes': {
                    '$sum': '$interaction.likes'
                },
                'comments': {
                    '$sum': '$interaction.comments'
                },
                'shares': {
                    '$sum': '$interaction.shares'
                }
            }
        }, {
            '$project': projection
        }
    ]
    return list(posts_collection.aggregate(aggregation))
