from graphene import ObjectType, Mutation, String, Schema, List, Field, Int, Boolean
from graphql.utils.ast_to_dict import ast_to_dict
from mongo_helper import retrieve_collections, retrieve_companies, retrieve_posts, retrieve_interactions, retrieve_interactions_from_post, retrieve_count_posts, retrieve_interactions, retrieve_evolution, insert_post, insert_interaction, update_company, update_post, update_interaction, retrieve_user
from functools import reduce
from loaders import UserLoader, InteractionLoader
from random import randrange
from bson import ObjectId


user_loader = UserLoader()
interaction_loader = InteractionLoader()


def collect_fields(node, fragments):
    field = {}

    if node.get('selection_set'):
        for leaf in node['selection_set']['selections']:
            if leaf['kind'] == 'Field':
                field.update({
                    leaf['name']['value']: collect_fields(leaf, fragments)
                })
            elif leaf['kind'] == 'FragmentSpread':
                field.update(collect_fields(fragments[leaf['name']['value']],
                                            fragments))

    return field


# Return the GraphQL query as a dictionary passing the info param
def get_fields(info):
    fragments = {}
    node = ast_to_dict(info.field_asts[0])

    for name, value in info.fragments.items():
        fragments[name] = ast_to_dict(value)

    return collect_fields(node, fragments)


class Interaction(ObjectType):
    _id = String()
    postId = String()
    source = String()
    likes = Int()
    comments = Int()
    shares = Int()
    date = String()


class UpdateInteraction(Mutation):
    class Arguments:
        _id = String(required=True)
        likes = Int()
        comments = Int()
        shares = Int()
        date = String()

    ok = Boolean()

    def mutate(root, info, **kwargs):
        _id = kwargs['_id']
        kwargs.pop('_id')
        if kwargs:
            update_interaction(_id, kwargs)
        return UpdateInteraction(ok=True if kwargs else False)


class User(ObjectType):
    name = String()
    address = String()


class Post(ObjectType):
    _id = String()
    companyId = String()
    text = String()
    date = String()
    source = String()
    interactions = Field(List(Interaction), page=Int())
    user = Field(User)

    def resolve_interactions(root, info, **kwargs):
        # Get pagination from GQL parameter
        page = kwargs.get('page', None)
        # Requested fields within a list
        requested_fields = list(get_fields(info))

        # Requested fields are reduced from an array of string to an array of objects { fieldNameInDb: True }
        # so that every field marked as true can be returned
        def reduce_func(acc, curr):
            if curr != 'Id':
                acc[curr] = True
            return acc

        projection = reduce(reduce_func, requested_fields, {'_id': True})
        # Get post_id from field
        post_id = root['_id']
        # Query to DB
        return interaction_loader.load(post_id)

    def resolve_user(root, info):
        # Requested fields within a list
        requested_fields = list(get_fields(info))

        # Requested fields are reduced from an array of string to an array of objects { fieldNameInDb: True }
        # so that every field marked as true can be returned
        def reduce_func(acc, curr):
            if curr != 'Id':
                acc[curr] = True
            return acc

        projection = reduce(reduce_func, requested_fields, {'_id': True})
        # Query to DB
        user_id = root['userId']
        # return retrieve_user(user_id, projection)
        return user_loader.load(user_id)


class CreatePost(Mutation):
    class Arguments:
        companyId = String(required=True)
        text = String(required=True)
        date = String(required=True)
        source = String(required=True)

    ok = Boolean()
    post = Field(Post)

    def mutate(root, info, **kwargs):
        kwargs['companyId'] = ObjectId(kwargs['companyId'])
        post = insert_post(kwargs)
        kwargs['_id'] = post.inserted_id
        interaction_args = {
            'postId': ObjectId(kwargs['_id']),
            'date': kwargs['date'],
            'likes': randrange(500),
            'comments': randrange(500),
            'shares': randrange(500)
        }
        interaction = insert_interaction(interaction_args)
        interaction_args['_id'] = interaction.inserted_id
        kwargs['interactions'] = [interaction_args]
        return {'ok': True, 'post': kwargs}


class UpdatePost(Mutation):
    class Arguments:
        _id = String(required=True)
        text = String()
        date = String()
        source = String()

    ok = Boolean()

    def mutate(root, info, **kwargs):
        _id = kwargs['_id']
        kwargs.pop('_id')
        if kwargs:
            update_post(_id, kwargs)
        return UpdatePost(ok=True if kwargs else False)


class Company(ObjectType):
    _id = String()
    name = String()
    followers = Int()
    posts = Field(List(Post), source=String(), page=Int())

    def resolve_posts(root, info, **kwargs):
        # Get source from GQL parameter
        source = kwargs.get('source', None)
        # Get pagination from GQL parameter
        page = kwargs.get('page', None)
        # Requested fields within a list
        requested_fields = list(get_fields(info))

        # Requested fields are reduced from an array of string to an array of objects { fieldNameInDb: True }
        # so that every field marked as true can be returned
        def reduce_func(acc, curr):
            if curr != 'Id':
                acc[curr] = True
            return acc

        projection = reduce(reduce_func, requested_fields, {'_id': True})
        if 'user' in requested_fields:
            projection['userId'] = 1
        # Get companyId from field
        companyId = root['_id']
        # Query to DB
        results = retrieve_posts(companyId, source, projection, page)
        return results


class UpdateCompany(Mutation):
    class Arguments:
        _id = String(required=True)
        followers = Int()
        name = String()

    ok = Boolean()

    def mutate(root, info, **kwargs):
        _id = kwargs['_id']
        kwargs.pop('_id')
        if kwargs:
            update_company(_id, kwargs)
        return UpdateCompany(ok=True if kwargs else False)


class CountPost(ObjectType):
    _id = String()
    number = Int()
    source = String()


class Evolution(ObjectType):
    week = Int()
    year = Int()
    source = String()
    likes = Int()
    comments = Int()
    shares = Int()


class Mutations(ObjectType):
    create_post = CreatePost.Field()
    update_company = UpdateCompany.Field()
    update_post = UpdatePost.Field()
    update_interaction = UpdateInteraction.Field()


class Query(ObjectType):
    companies = Field(List(Company), _id=String(), page=Int())
    count_posts = Field(CountPost, _id=String(
        required=True), source=String())
    interactions = Field(List(Interaction), _id=String(required=True))
    evolution = Field(List(Evolution), _id=String(required=True))

    def resolve_companies(root, info, **kwargs):
        # Get _id from GQL parameter
        _id = kwargs.get('_id', None)
        # Get pagination from GQL parameter
        page = kwargs.get('page', None)
        # Requested fields within a list
        requested_fields = list(get_fields(info))

        # Requested fields are reduced from an array of string to an array of objects { fieldNameInDb: True }
        # so that every field marked as true can be returned
        def reduce_func(acc, curr):
            if curr != 'Id':
                acc[curr] = True
            return acc

        projection = reduce(reduce_func, requested_fields, {'_id': True})
        # Query to DB
        results = retrieve_companies(_id, projection, page)
        return results

    def resolve_count_posts(root, info, **kwargs):
        # Get _id from GQL parameter
        _id = kwargs['_id']
        # Get source from GQL parameter
        source = kwargs.get('source', None)
        # Query to DB
        result = retrieve_count_posts(_id, source)[0]
        return result

    def resolve_interactions(root, info, **kwargs):
        # Get _id from GQL parameter
        _id = kwargs['_id']
        # Requested fields within a list
        requested_fields = list(get_fields(info))

        # Requested fields are reduced from an array of string to an array of objects { fieldNameInDb: True }
        # so that every field marked as true can be returned
        def reduce_func(acc, curr):
            if curr != 'Id':
                if curr == 'source':
                    acc[curr] = "$_id.source"
                else:
                    acc[curr] = True
            return acc

        reduced_fields = reduce(reduce_func, requested_fields, {'_id': True})
        # Query to DB
        results = retrieve_interactions(_id, reduced_fields)
        return results

    def resolve_evolution(root, info, **kwargs):
        # Get _id from GQL parameter
        _id = kwargs['_id']
        # Requested fields within a list
        requested_fields = list(get_fields(info))
        # Projected fields structure
        projection = {
            'week': '$_id.week',
            'year': '$_id.year',
            'source': '$_id.source',
            'likes': '$likes',
            'comments': '$comments',
            'shares': '$shares'
        }

        # Requested fields are reduced from an array of string to an array of objects { fieldNameInDb: True }
        # so that every field marked as true can be returned
        def reduce_func(acc, curr):
            if curr != 'Id':
                acc[curr] = projection.get(curr, False)
            return acc

        reduced_fields = reduce(reduce_func, requested_fields, {'_id': False})
        results = retrieve_evolution(_id, reduced_fields)
        return results


schema = Schema(query=Query, mutation=Mutations)
