from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")  # or your Atlas URL

db = client["price_comparison"]
collection = db["products"]
