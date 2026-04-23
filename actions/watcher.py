import time
from minio import Minio
from thumbnail_gen import main as process_image

# 1. MinIO connection setup
client = Minio(
    "localhost:9000", 
    access_key="admin", 
    secret_key="password123", 
    secure=False
)

print("👀 Group 18 Watcher is active... Monitoring 'uploads' bucket.")

# Pehle se majood files ki list (taake purani process na hon)
processed_files = set()

# Start mein jo files hain unhe note kar lo
try:
    existing_items = client.list_objects("uploads")
    for item in existing_items:
        processed_files.add(item.object_name)
except:
    print("⚠️  Uploads bucket abhi khali hai ya nahi bani.")

while True:
    try:
        # 2. Check for new files in 'uploads' bucket
        objects = client.list_objects("uploads")
        
        for obj in objects:
            if obj.object_name not in processed_files:
                print(f"🚀 Nayi image detect hui: {obj.object_name}!")
                
                # 3. Code ko trigger karna (Automatic process)
                result = process_image({"bucket": "uploads", "key": obj.object_name})
                
                print(f"✅ Result: {result['message']}")
                
                # File ko 'done' list mein daal dena
                processed_files.add(obj.object_name)
        
    except Exception as e:
        print(f"❌ Error during watching: {e}")
        
    time.sleep(3) # Har 3 second baad check karo