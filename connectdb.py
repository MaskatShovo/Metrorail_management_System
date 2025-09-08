from pymongo import MongoClient

# Your credentials
username = "syedalamimaislam_db_user"
password = "52Vg7y0FY1VEE43H"

# Your MongoDB Atlas connection URI
uri = f"mongodb+srv://{username}:{password}@cluster0.ssm825h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    # Create MongoDB client
    client = MongoClient(uri)

    # ✅ Replace 'test' with your actual database name
    db = client["test"]

    # ✅ Replace 'your_collection_name' with your actual collection name
    collection = db["your_collection_name"]

    # Example: Fetch and print all documents
    for doc in collection.find():
        print(doc)

    print("✅ Successfully connected to MongoDB!")

except Exception as e:
    print("❌ Failed to connect to MongoDB:")
    print(e)
