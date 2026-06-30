import os
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])



load_dotenv() # Loads SUPABASE_URL and KEY from your .env file

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def ingest_lead(data):
    """Upserts a property and returns its ID."""
    result = supabase.table("properties").upsert(
        {"address": data["address"], "postcode": data["postcode"], "owner_name": data["owner_name"], "source_type": data["source_type"]},
        on_conflict="address,postcode"
    ).execute()
    return result.data[0]['id']

def process_new_lead(property_data, signals):
    """Links a property to one or more signals and returns total score."""
    pid = ingest_lead(property_data)
    total_score = 0
    for s in signals:
        supabase.table("lead_signals").insert({
            "property_id": pid,
            "signal_type": s['type'],
            "severity_score": s['score']
        }).execute()
        total_score += s['score']
    return total_score

def get_matching_investors(property_id=None):
    """Logic to match property attributes to investor criteria.Fetches investors. If property_id is None, return all."""
    # This is a placeholder for your matching engine logic
    return supabase.table("investors").select("*").execute().data
    # 1. Get the property details first
    # prop = supabase.table("properties").select("*").eq("id", property_id).single().execute().data
    
    # 2. Query investors whose 'criteria' contains the property's 'source_type' or 'postcode'
    # This is a basic filter; you can make this much more complex
    # return supabase.table("investors").select("*").ilike("criteria", f"%{prop['source_type']}%").execute().data

def ingest_distressed_data(df):
    #df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        # 1. Upsert Property
        property_data = {
            "address": row['address'],
            "postcode": row['postcode'],
            "owner_name": row['owner_name'],
            "source_type": row['source_type']
        }
        
        # Use .upsert with on_conflict to prevent duplicates
        result = supabase.table("properties").upsert(
            property_data, on_conflict="address,postcode"
        ).execute()
        
        # 2. Insert Signal
        property_id = result.data[0]['id']
        signal_data = {
            "property_id": property_id,
            "signal_type": row['signal_type'],
            "severity_score": row['severity_score']
        }
        supabase.table("lead_signals").insert(signal_data).execute()

def get_hottest_deals():
    # 1. Fetch ALL signal data
    signals = supabase.table("lead_signals").select("property_id, severity_score").execute().data
    
    if not signals:
        print("DEBUG: No signals found in database.")
        return []

    # 2. Group scores by property_id
    scores = {}
    for s in signals:
        pid = s['property_id']
        scores[pid] = scores.get(pid, 0) + s['severity_score']
    
    # 3. Fetch properties that have signals
    p_ids = list(scores.keys())
    properties = supabase.table("properties").select("id, address, postcode, status").in_("id", p_ids).execute().data
    
    # 4. Add the score to the property dictionary
    for p in properties:
        p['total_score'] = scores.get(p['id'], 0)
        
    return sorted(properties, key=lambda x: x['total_score'], reverse=True)

def update_property_status(property_id, new_status):
    """
    Updates the status column of a specific property in Supabase.
    """
    try:
        response = supabase.table("properties") \
            .update({"status": new_status}) \
            .eq("id", property_id) \
            .execute()
        return response
    except Exception as e:
        print(f"DEBUG: Error updating status for {property_id}: {e}")
        return None