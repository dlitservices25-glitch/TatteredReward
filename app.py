import streamlit as st
from PIL import Image
import pandas as pd
from db_manager import ingest_distressed_data, get_matching_investors, get_hottest_deals, update_property_status

st.write(f"DEBUG: Session state logged_in: {st.session_state.get('logged_in', False)}")

# Initialize session state for auth
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def main():
    im = Image.open("favicon.ico")
    st.set_page_config(
      page_title="Hello",
      page_icon=im,
      layout="wide",
    )

    if not st.session_state.logged_in:
        # --- AUTHENTICATION PAGE ---
        st.title("Login / Sign Up")
        # Your auth forms go here
        if st.button("Simulate Login"):
            st.session_state.logged_in = True
            st.rerun() # Forces the app to reload and show the dashboard
    else:
        # --- DASHBOARD PAGE ---
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(logged_in=False))
        
        st.set_page_config(page_title="Property Sourcing", layout="wide")
        
        st.title("Property Sourcing Command Center")

        # Now show your tabs
        # Tabs for navigation
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Dashboard", "Deal Pipeline", "Pipeline", "Ingestion", "Hot Leads", "Investor CRM"])

        with tab1:
            st.header("Dashboard Metrics 📊")
            st.write("Overview of your distressed property pipeline.")
            # In your app.py, inside the logged-in dashboard block

            # 1. KPI Row (The "Quick Stats")
            deals = get_hottest_deals()
            col1, col2, col3 = st.columns(3)

            if deals:
                df = pd.DataFrame(deals)
                col1.metric("Total Leads", len(df))
                col2.metric("Hot Leads (>10pts)", len(df[df['total_score'] > 10]))
                col3.metric("Avg Motivation", round(df['total_score'].mean(), 1))
            else:
                col1.metric("Total Leads", 0)

            # 2. The Main Pipeline Table
            st.subheader("Priority Deal Pipeline")

            # In app.py
            if deals:
                df = pd.DataFrame(deals)
    
                # 1. Ensure 'id' is in the dataframe so we can reference it for updates
                # 2. Rename columns for the display table
                display_df = df[['id', 'address', 'postcode', 'total_score', 'status']]
    
                edited_df = st.data_editor(
                    display_df,
                    key="my_editor",
                    column_config={
                        "id": st.column_config.Column(disabled=True), # Hide/Disable editing the ID
                        "status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["New", "Contacted", "Offer Made", "Dead"],
                            required=True,
                        )
                    },
                    hide_index=True
                )
    
                if st.button("Save Changes"):
                    # Safely check if the editor has captured any edits
                    if "my_editor" in st.session_state:
                        # Now it's safe to access
                        edited_data = st.session_state.my_editor
    
                        # Access the 'edited_rows' dictionary
                        if "edited_rows" in edited_data:
                            changes = edited_data["edited_rows"]
                            st.write("Changes detected:", changes)
    
                            # Logic to process updates...
                            # Now you are looking at the data exactly as the user left it
                            for _, row in edited_df.iterrows():
                                update_property_status(row['id'], row['status'])
                        else:
                            st.info("No changes were made to the table.")
                    else:
                        st.error("The editor has not been initialized yet.")

        with tab2:
            st.header("Qualified Motivated Sellers")
            # You will later call your Supabase functions here
            st.write("Displaying database results...")

        with tab3:
            st.header("Active Deal Pipeline")
            # You can fetch and display your data here
            # data = supabase.table("properties").select("*, lead_signals(*)").execute()
            st.write("Displaying qualified deals from Supabase...")
        
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
        
        with tab6:
            st.header("Investor List")
            st.write("Matching properties to investor profiles.")
            investors = get_matching_investors()

            # Debugging: Print to terminal
            print(f"DEBUG: Data received from DB: {investors}")

            if not investors:
                st.warning("The 'investors' table is empty or could not be reached.")
            else:
                st.dataframe(pd.DataFrame(investors))

if __name__ == "__main__":
    main()