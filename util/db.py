from pymongo import MongoClient

import config

client = MongoClient(config.MONGODB_URL)

devices = client[config.MONGODB_COLLECTION]['devices']
domains = client[config.MONGODB_COLLECTION]['domains']

devices.create_index(['id'])
domains.create_index(['domain'])


def get_device_by_id(device_id):
    return devices.find_one({'id': device_id})


def create_device(entry):
    return devices.insert_one(entry)


def update_device_code(id, code):
    return devices.update_one({'id': id}, {'$set': {'code': code}})


def update_device_tokens(id, token, refresh):
    return devices.update_one({'id': id}, {'$set': {'token': token, 'refresh': refresh}})


def update_tokens(token, param, param1):
    return devices.update_one({'token': token}, {'$set': {'token': param, 'refresh': param1}})


def delete_device(id):
    return devices.delete_one({'id': id})


def update_device_settings(id, param):
    return devices.update_one({'id': id}, {'$set': {'settings': param}})


def get_domain(domain):
    return domains.find_one({'domain': domain})

def add_domain(domain):
    domains.insert_one({'domain': domain})

