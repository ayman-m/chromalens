"""
Dashboard page for ChromaLens UI
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

from components.header import show_success, show_error, show_info, show_warning
from components.utils import format_timestamp, truncate_text

def render_dashboard():
    """Render the dashboard page"""
    st.header("Dashboard")
    
    # Show server stats
    render_server_stats()
    
    # Show collections overview
    render_collections_overview()
    
    # Show recent activity (if available)
    render_recent_activity()

def render_server_stats():
    """Render server statistics"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tenants", len(st.session_state.tenants))
    
    with col2:
        st.metric("Databases", len(st.session_state.databases))
    
    with col3:
        st.metric("Collections", len(st.session_state.collections))
    
    # Server information
    st.subheader("Server Information")
    try:
        version = st.session_state.client.heartbeat()
        
        server_info = {
            "Version": version if isinstance(version, str) else "Unknown",
            "Connected to": f"{st.session_state.connection_params['host']}:{st.session_state.connection_params['port']}",
            "Tenant": st.session_state.connection_params['tenant'],
            "Database": st.session_state.connection_params['database'],
            "Last refreshed": st.session_state.last_refresh.strftime("%H:%M:%S") if st.session_state.last_refresh else "Never"
        }
        
        # Display as a nice info box
        info_text = "\n".join([f"**{k}:** {v}" for k, v in server_info.items()])
        st.markdown(f"""
        <div style="padding: 1rem; background-color: #D6EAF8; border-radius: 0.5rem; border-left: 0.5rem solid #3498DB;">
            {info_text}
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Failed to get server information: {e}")

def render_collections_overview():
    """Render collections overview"""
    st.subheader("Collections")
    
    if not st.session_state.collections:
        st.info(f"No collections found in database '{st.session_state.connection_params['database']}'")
        return
    
    # Create a DataFrame for collections
    collections_df = pd.DataFrame([
        {
            "Name": c.get("name"),
            "ID": c.get("id"),
            "Dimension": c.get("dimension"),
            "Has Metadata": "Yes" if c.get("metadata") else "No",
            "Description": c.get("metadata", {}).get("description", "")
        }
        for c in st.session_state.collections
    ])
    
    # Display as a table
    st.dataframe(collections_df, use_container_width=True)
    
    # If we have count information for collections, show a bar chart
    try:
        # Get item counts for collections (if the client supports it)
        collection_stats = []
        for collection in st.session_state.collections:
            try:
                name = collection.get("name", "")
                count = st.session_state.client.get_collection_stats(
                    collection_name=name,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                ).get("count", 0)
                
                collection_stats.append({
                    "Collection": name,
                    "Items": count
                })
            except Exception:
                # Skip collections that don't have stats
                pass
        
        if collection_stats:
            stats_df = pd.DataFrame(collection_stats)
            
            # Create bar chart
            chart = alt.Chart(stats_df).mark_bar().encode(
                x='Collection',
                y='Items',
                color=alt.Color('Collection', legend=None),
                tooltip=['Collection', 'Items']
            ).properties(
                title='Items per Collection',
                width='container'
            )
            
            st.altair_chart(chart, use_container_width=True)
    except Exception:
        # Don't display chart if there's an error
        pass

def render_recent_activity():
    """Render recent activity section (placeholder)"""
    st.subheader("Recent Activity")
    
    # This would typically be populated with real activity data
    # For now, we'll just show a placeholder
    
    activity_data = [
        {"timestamp": datetime.now().timestamp() - 3600, "action": "Collection created", "details": "test_collection"},
        {"timestamp": datetime.now().timestamp() - 7200, "action": "Items added", "details": "50 items added to collection 'embeddings'"},
        {"timestamp": datetime.now().timestamp() - 10800, "action": "Query executed", "details": "Semantic search in 'documents'"}
    ]
    
    if activity_data:
        # Format the data
        formatted_activity = [{
            "Time": format_timestamp(item["timestamp"]),
            "Action": item["action"],
            "Details": item["details"]
        } for item in activity_data]
        
        # Display as a table
        st.dataframe(
            pd.DataFrame(formatted_activity),
            use_container_width=True
        )
    else:
        st.info("No recent activity to display")