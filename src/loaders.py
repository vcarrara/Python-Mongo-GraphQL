from promise import Promise
from promise.dataloader import DataLoader
from mongo_helper import retrieve_user, retrieve_users, retrieve_interactions_from_posts


class UserLoader(DataLoader):
    def batch_load_fn(self, keys):
        return Promise.resolve(retrieve_users(keys))


class InteractionLoader(DataLoader):
    def batch_load_fn(self, keys):
        return Promise.resolve(retrieve_interactions_from_posts(keys))
