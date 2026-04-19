from pymongo import MongoClient

from llm import LLM


class TaskContext:
    db: MongoClient
    llm: LLM
