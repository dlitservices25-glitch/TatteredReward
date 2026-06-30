import os
from supabase import create_client
from dotenv import load_dotenv

# 1. Load your variables
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# 2. Basic Debugging
print(f"Connecting to: {url}")
if not url or not key:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_KEY in .env file.")
else:
    try:
        # 3. Attempt connection
        supabase = create_client(url, key)
        
        # 4. Attempt a simple fetch from a known table (like properties)
        # We use .limit(1) so it's very lightweight
        response = supabase.table("properties").select("*").limit(1).execute()
        
        print("SUCCESS: Connection to Supabase is working!")
        print(f"Data returned: {response.data}")
        
    except Exception as e:
        print(f"CONNECTION FAILED: {e}")