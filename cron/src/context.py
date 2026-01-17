from pymongo import MongoClient


class TaskContext:
    db: MongoClient
