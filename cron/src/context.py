from pymongo import MongoClient

from common.python.llm import LLM


class TaskContext:
    db: MongoClient
    llm: LLM
