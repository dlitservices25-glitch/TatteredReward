import streamlit as st
import pandas as pd
from db_manager import ingest_distressed_data, get_matching_investors, get_hottest_deals

st.set_page_config(page_title="Property Sourcing", layout="wide")

st.title("Property Sourcing Command Center")

# Tabs for navigation
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Dashboard", "Deal Pipeline", "Investor CRM", "Ingestion", "Pipeline", "Hot Leads"])

with tab1:
    st.header("Dashboard Metrics")
    st.write("Overview of your distressed property pipeline.")

with tab2:
    st.header("Qualified Motivated Sellers")
    # You will later call your Supabase functions here
    st.write("Displaying database results...")

with tab3:
    st.header("Investor List")
    st.write("Matching properties to investor profiles.")
    investors = get_matching_investors()
    
    # Debugging: Print to terminal
    print(f"DEBUG: Data received from DB: {investors}")
    
    if not investors:
        st.warning("The 'investors' table is empty or could not be reached.")
    else:
        st.dataframe(pd.DataFrame(investors))

with tab4:
    uploaded_file = st.file_uploader("Upload Distressed CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head()) # Helpful to see what's being uploaded
        if st.button("Process Data"):
            with st.spinner("Syncing to Supabase..."):
                ingest_distressed_data(df)
                st.success("Data successfully synced to Supabase!")

with tab5:
    st.header("Active Deal Pipeline")
    # You can fetch and display your data here
    # data = supabase.table("properties").select("*, lead_signals(*)").execute()
    st.write("Displaying qualified deals from Supabase...")

with tab6:
    st.header("🔥 Property Priority Queue")

    deals = get_hottest_deals()

    if deals and isinstance(deals, list):
        df_deals = pd.DataFrame(deals)
    
        # Add a visual indicator
        st.dataframe(
            df_deals.style.background_gradient(subset=['total_score'], cmap='OrRd'),
            use_container_width=True
        )
    else:
        st.info("No leads processed yet. Upload a CSV to get started!")