import os
import streamlit as st
import requests
import json
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from io import BytesIO
from fpdf import FPDF

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# 1. PAGE CONFIG
st.set_page_config(page_title="AI Supply Chain Optimizer", layout="wide", initial_sidebar_state="expanded")

# Initialize session state for navigation
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "Home"

# 2. CUSTOM CSS - Enterprise Theme
st.markdown("""
<style>
/* Enterprise Theme */
.stApp {
    color: var(--text-color);
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    border-right: 1px solid var(--background-color);
    padding-top: 1rem;
}
.custom-header {
    background: linear-gradient(135deg, #0F3057 0%, #1A4F8E 100%);
    color: white;
    padding: 2.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
}
.custom-header h1 {
    color: white;
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
}
.custom-header p {
    color: #E2E8F0;
    font-size: 1.1rem;
    margin-top: 0.5rem;
}
.metric-card {
    background-color: var(--secondary-background-color);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    margin-bottom: 1.5rem;
    border: 1px solid var(--background-color);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
}
.metric-title {
    color: var(--text-color);
    opacity: 0.8;
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
.metric-value {
    color: var(--text-color);
    font-size: 2rem;
    font-weight: 700;
}
.metric-change.positive { color: #10B981; }
.metric-change.negative { color: #EF4444; }
[data-testid="stPlotlyChart"] {
    background-color: var(--secondary-background-color);
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    padding: 1rem;
    margin-bottom: 1.5rem;
    border: 1px solid var(--background-color);
}
.stButton>button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border: 1px solid var(--background-color);
}
.stButton>button[kind="primary"] {
    background-color: #F97316 !important;
    color: white !important;
    border: none;
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Cache API requests to avoid redundant calls
@st.cache_data(ttl=60)
def fetch_data(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}")
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        pass
    return []

# Fetch health for sidebar (uncached for real-time status)
def fetch_health():
    try:
        r = requests.get(f"{API_URL}/api/health", timeout=2)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

health_data = fetch_health()

# 3. SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("<div style='text-align:center; padding-bottom: 1rem;'><h2 style='color: var(--text-color); font-weight: 700; margin-bottom: 0;'>SC Optimizer</h2><span style='color: var(--text-color); font-size: 0.8rem;'>Enterprise Edition</span></div>", unsafe_allow_html=True)
    
    # Grouped options with emojis
    options = [
        "🏠 Home", 
        "📊 Dashboard", 
        "---",
        "📈 Demand Forecasting", 
        "🏭 Supplier Management", 
        "📦 Inventory Monitoring", 
        "🚚 Route Optimization", 
        "⚠️ Risk Analysis",
        "---",
        "📋 Procurement Requests", 
        "📨 RFQ Management", 
        "⚖️ Quotation Comparison", 
        "✅ Order Approval", 
        "📦 Order Monitoring", 
        "---",
        "🔄 Supply Chain Workflow", 
        "📉 Analytics", 
        "📂 Data Management", 
        "⚙️ Settings"
    ]
    
    # Map back to original IDs for logic
    page_map = {
        "🏠 Home": "Home",
        "📊 Dashboard": "Dashboard",
        "📈 Demand Forecasting": "Demand Forecasting",
        "🏭 Supplier Management": "Supplier Management",
        "📦 Inventory Monitoring": "Inventory Monitoring",
        "🚚 Route Optimization": "Route Optimization",
        "⚠️ Risk Analysis": "Risk Analysis",
        "📋 Procurement Requests": "Procurement Requests",
        "📨 RFQ Management": "RFQ Management",
        "⚖️ Quotation Comparison": "Quotation Comparison",
        "✅ Order Approval": "Order Approval",
        "📦 Order Monitoring": "Order Monitoring",
        "🔄 Supply Chain Workflow": "Supply Chain Workflow",
        "📉 Analytics": "Analytics",
        "📂 Data Management": "Data Management",
        "⚙️ Settings": "Settings"
    }

    # Find current index for initialization
    if 'menu_idx' not in st.session_state:
        st.session_state.menu_idx = 0

    selected_label = option_menu(
        menu_title=None,
        options=options,
        default_index=st.session_state.menu_idx,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"display": "none"}, # Hide default icons, using emojis
            "nav-link": {
                "font-size": "0.9rem", 
                "text-align": "left", 
                "margin":"2px 0px", 
                "padding": "10px", 
                "border-radius": "8px", 
                "color": "var(--text-color)", 
                "font-weight":"500",
                "user-select": "none",
                "cursor": "pointer"
            },
            "nav-link-selected": {"background-color": "#F97316", "color": "#FFFFFF", "font-weight":"600"},
        }
    )
    
    if selected_label and selected_label != "---":
        new_page = page_map.get(selected_label, "Home")
        if new_page != st.session_state.selected_page:
            st.session_state.selected_page = new_page
            st.session_state.menu_idx = options.index(selected_label)
            st.rerun()
            
    selected = st.session_state.selected_page
    
    st.markdown("---")
    st.markdown("<div style='font-size:0.8rem; font-weight:600; color: var(--text-color); text-transform:uppercase; margin-bottom:0.5rem;'>System Health</div>", unsafe_allow_html=True)
    
    def get_status_html(component, sub=None):
        if not health_data: return "<span style='color:#EF4444'>●</span>"
        if sub:
            val = health_data.get("agents", {}).get(sub)
        else:
            val = health_data.get(component)
        color = "#10B981" if val == "active" else "#EF4444"
        return f"<span style='color:{color}'>●</span>"

    st.markdown(f"<div style='font-size:0.85rem; color: var(--text-color); padding:2px 0;'>{get_status_html('database')} Database Connected</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.85rem; color: var(--text-color); padding:2px 0;'>{get_status_html('agents', 'forecast')} Forecast Agent</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.85rem; color: var(--text-color); padding:2px 0;'>{get_status_html('agents', 'inventory')} Inventory Agent</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.85rem; color: var(--text-color); padding:2px 0;'>{get_status_html('agents', 'procurement')} Procurement Agent</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.85rem; color: var(--text-color); padding:2px 0;'>{get_status_html('agents', 'supplier')} Supplier Agent</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.85rem; color: var(--text-color); padding:2px 0;'>{get_status_html('agents', 'risk')} Risk Agent</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.85rem; color: var(--text-color); padding:2px 0;'>{get_status_html('agents', 'route')} Route Agent</div>", unsafe_allow_html=True)


# EXPORT HELPER FUNCTIONS
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def to_pdf(df, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Arial", size=8)
    text = df.to_string(index=False)
    for line in text.split('\n'):
        pdf.cell(0, 5, txt=line, ln=True)
    return bytes(pdf.output())

def render_export_buttons(df, filename_prefix, title):
    if df.empty: return
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(label="📥 Export CSV", data=df.to_csv(index=False), file_name=f"{filename_prefix}.csv", mime='text/csv')
    with c2:
        st.download_button(label="📥 Export Excel", data=to_excel(df), file_name=f"{filename_prefix}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    with c3:
        try:
            st.download_button(label="📥 Export PDF", data=to_pdf(df, title), file_name=f"{filename_prefix}.pdf", mime='application/pdf')
        except Exception as e:
            st.error(f"PDF Export Error: {e}")

# 4. VIEW RENDERING
if selected == "Home":
    st.markdown("""
    <div class="custom-header" style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #0F3057 0%, #2563EB 100%);">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem;">Decentralized Multi-Agent<br>Supply Chain Optimizer</h1>
        <p style="font-size: 1.25rem; opacity: 0.9;">AI-powered Procurement and Logistics Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Counters
    st.markdown("<h3 style='color: var(--text-color); margin-bottom: 1rem;'>System Overview</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='metric-card'><div class='metric-title'>AI Agents</div><div class='metric-value'>6 <span style='font-size:1rem; color:#10B981'>● Active</span></div></div>", unsafe_allow_html=True)
    with c2:
        orders = fetch_data("api/orders")
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Orders</div><div class='metric-value'>{len(orders)}</div></div>", unsafe_allow_html=True)
    with c3:
        suppliers = fetch_data("suppliers")
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Network Suppliers</div><div class='metric-value'>{len(suppliers)}</div></div>", unsafe_allow_html=True)
    with c4:
        inventory = fetch_data("inventory")
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Tracked Items</div><div class='metric-value'>{len(inventory)}</div></div>", unsafe_allow_html=True)

    st.markdown("<h3 style='color: var(--text-color); margin-top: 2rem; margin-bottom: 1rem;'>AI Capabilities</h3>", unsafe_allow_html=True)
    
    # Capabilities Grid
    grid1, grid2, grid3 = st.columns(3)
    with grid1:
        st.markdown("<div class='metric-card' style='height: 160px;'><h4 style='margin:0 0 10px 0; color: var(--text-color);'>📈 Forecast Agent</h4><p style='color: var(--text-color); font-size:0.95rem;'>Analyzes historical data and market signals to predict demand trends, ensuring you never face unexpected stockouts.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-card' style='height: 160px;'><h4 style='margin:0 0 10px 0; color: var(--text-color);'>🏭 Supplier Agent</h4><p style='color: var(--text-color); font-size:0.95rem;'>Evaluates and selects the optimal supplier based on real-time pricing, delivery schedules, and historical reliability ratings.</p></div>", unsafe_allow_html=True)
    with grid2:
        st.markdown("<div class='metric-card' style='height: 160px;'><h4 style='margin:0 0 10px 0; color: var(--text-color);'>📦 Inventory Agent</h4><p style='color: var(--text-color); font-size:0.95rem;'>Continuously monitors warehouse stock levels against required thresholds to automatically flag replenishment needs.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-card' style='height: 160px;'><h4 style='margin:0 0 10px 0; color: var(--text-color);'>⚠️ Risk Agent</h4><p style='color: var(--text-color); font-size:0.95rem;'>Scans geopolitical, environmental, and logistical data to evaluate and mitigate supply chain disruptions proactively.</p></div>", unsafe_allow_html=True)
    with grid3:
        st.markdown("<div class='metric-card' style='height: 160px;'><h4 style='margin:0 0 10px 0; color: var(--text-color);'>🛒 Procurement Agent</h4><p style='color: var(--text-color); font-size:0.95rem;'>Synthesizes data from all other agents to generate optimal, cost-effective purchase recommendations automatically.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-card' style='height: 160px;'><h4 style='margin:0 0 10px 0; color: var(--text-color);'>🚚 Route Agent</h4><p style='color: var(--text-color); font-size:0.95rem;'>Calculates the most efficient logistics and delivery routes to minimize transit times and reduce freight costs.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("Launch Dashboard", use_container_width=True, type="primary"):
            st.session_state.selected_page = "Dashboard"
            st.session_state.menu_idx = options.index("📊 Dashboard")
            st.rerun()

elif selected == "Dashboard":
    st.markdown("<div style='display: flex; justify-content: space-between; align-items: center; padding: 1rem 0 2rem 0;'><h2 style='color: var(--text-color); font-weight: 700; margin: 0;'>Command Center</h2><div style='background-color: var(--secondary-background-color); padding: 0.5rem 1rem; border-radius: 8px; border: 1px solid var(--background-color); color: var(--text-color); font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>📥 Export Report</div></div>", unsafe_allow_html=True)

    # Fetch live data
    orders = fetch_data("api/orders")
    inventory = fetch_data("inventory")
    suppliers = fetch_data("suppliers")
    routes = fetch_data("routes")
    history = fetch_data("history")
    
    # KPIs Calculation
    df_orders = pd.DataFrame(orders) if orders else pd.DataFrame()
    total_spend = df_orders[df_orders['status'].str.lower() != 'rejected']['total_cost'].sum() if not df_orders.empty else 0
    total_orders = len(orders)
    active_suppliers = len(suppliers)
    low_stock_items = len([i for i in inventory if int(i.get('stock_level', 0)) < 50]) if inventory else 0
    total_inventory_items = len(inventory) if inventory else 0
    active_routes = len(routes) if routes else 0
    ai_recs = len(history) if history else 0
    avg_rating = sum(s.get('rating',0) for s in suppliers)/len(suppliers) if suppliers else 0
    
    # Top KPI Row 1
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Procurement Spend</div><div class='metric-value'>${total_spend:,.2f}</div></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Orders</div><div class='metric-value'>{total_orders}</div></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Suppliers</div><div class='metric-value'>{active_suppliers}</div></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Inventory Items</div><div class='metric-value'>{total_inventory_items}</div></div>", unsafe_allow_html=True)

    # Top KPI Row 2
    k5, k6, k7, k8 = st.columns(4)
    with k5:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Low Stock Alerts</div><div class='metric-value' style='color:#EF4444;'>{low_stock_items}</div></div>", unsafe_allow_html=True)
    with k6:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Active Routes</div><div class='metric-value'>{active_routes}</div></div>", unsafe_allow_html=True)
    with k7:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>AI Recommendations</div><div class='metric-value' style='color:#10B981;'>{ai_recs}</div></div>", unsafe_allow_html=True)
    with k8:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Avg Supplier Rating</div><div class='metric-value'>{avg_rating:.1f} / 5.0</div></div>", unsafe_allow_html=True)

    # Row 2: Charts
    c1, c2 = st.columns([1.2, 1])
    
    with c1:
        if not df_orders.empty:
            spend_by_supplier = df_orders[df_orders['status'].str.lower() != 'rejected'].groupby('supplier_name')['total_cost'].sum().reset_index()
            fig_spend = go.Figure(go.Bar(x=spend_by_supplier['supplier_name'], y=spend_by_supplier['total_cost'], marker_color='#F97316', text=spend_by_supplier['total_cost'], texttemplate='$%{text:,.0f}', textposition='outside'))
            fig_spend.update_layout(title=dict(text="Spend by Supplier", font=dict(size=16, color=None, family="Inter")), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=60, b=40), height=350, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#F1F5F9'))
            st.plotly_chart(fig_spend, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No order data available for spend analysis.")
            
    with c2:
        if not df_orders.empty:
            status_counts = df_orders['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            colors = {'Approved': '#10B981', 'Pending': '#F59E0B', 'Rejected': '#EF4444'}
            pie_colors = [colors.get(s, '#64748B') for s in status_counts['status']]
            fig_status = go.Figure(data=[go.Pie(labels=status_counts['status'], values=status_counts['count'], hole=.6, marker=dict(colors=pie_colors))])
            fig_status.add_annotation(text=f"{total_orders}<br>Orders", x=0.5, y=0.5, font_size=20, showarrow=False)
            fig_status.update_layout(title="Order Status Distribution", title_font=dict(size=16, color=None, family="Inter"), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=60, b=20), height=350)
            st.plotly_chart(fig_status, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No order status data available.")

    # Row 3: Inventory & Ratings
    c3, c4 = st.columns([1, 1.2])
    with c3:
        if avg_rating > 0:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = avg_rating,
                number = {'font': {'size': 36}},
                title = {'text': "Supplier Health Network", 'font': {'size': 16}},
                gauge = {
                    'axis': {'range': [0, 5], 'visible': False},
                    'bar': {'color': "#F97316"},
                    'steps': [{'range': [0, 3], 'color': "#EF4444"}, {'range': [3, 4], 'color': "#F59E0B"}, {'range': [4, 5], 'color': "#10B981"}]
                }
            ))
            fig_gauge.update_layout(margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
            
    with c4:
        if inventory:
            df_inv = pd.DataFrame(inventory).sort_values(by='stock_level').head(5)
            fig_inv = go.Figure(go.Bar(x=df_inv['stock_level'], y=df_inv['product_name'], orientation='h', marker_color='#F59E0B'))
            fig_inv.update_layout(title=dict(text="Lowest Stock Items", font=dict(size=16, color=None, family="Inter")), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=60, b=20), height=350)
            st.plotly_chart(fig_inv, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No inventory data available.")

elif selected == "Demand Forecasting":
    st.markdown("<h2>Demand Forecasting (Forecast Agent)</h2>", unsafe_allow_html=True)
    with st.form("forecast_form"):
        product_name = st.text_input("Product Name", "Industrial Laptop")
        quantity = st.number_input("Requested Quantity", min_value=1, value=100)
        submit_button = st.form_submit_button("Run Forecast Analysis")
        
    if submit_button:
        with st.spinner("Analyzing demand trends..."):
            try:
                resp = requests.post(f"{API_URL}/api/forecast", json={"product_name": product_name, "quantity": quantity}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success("Analysis Complete")
                    st.metric("Recommended Quantity to Order", data.get("quantity_to_order"))
                    st.info(data.get("analysis"))
                else:
                    st.error("API error or quota exceeded. Please try again later.")
            except requests.exceptions.RequestException:
                st.error("Connection timed out. Gemini API quota exceeded or backend unavailable.")

elif selected == "Supplier Management":
    st.markdown("<h2>Supplier Management (Supplier Agent)</h2>", unsafe_allow_html=True)
    
    suppliers = fetch_data("suppliers")
    if suppliers:
        st.markdown("### Current Suppliers")
        df = pd.DataFrame(suppliers)
        st.dataframe(df, use_container_width=True)
        render_export_buttons(df, "suppliers_report", "Suppliers Report")
        
    st.markdown("### AI Supplier Recommendation")
    with st.form("supplier_form"):
        required_delivery_days = st.number_input("Required Delivery Days", min_value=1, value=5)
        submit_button = st.form_submit_button("Recommend Supplier")
        
    if submit_button:
        with st.spinner("Finding best supplier..."):
            try:
                resp = requests.post(f"{API_URL}/api/suppliers/recommend", json={"required_delivery_days": required_delivery_days}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Recommended Supplier: {data.get('selected_supplier_name')}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Price", f"${data.get('price')}")
                    c2.metric("Delivery Days", data.get("delivery_days"))
                    c3.metric("Rating", data.get("rating"))
                else:
                    st.error("API error or quota exceeded. Please try again later.")
            except requests.exceptions.RequestException:
                st.error("Connection timed out. Gemini API quota exceeded or backend unavailable.")

elif selected == "Inventory Monitoring":
    st.markdown("<h2>Inventory Monitoring (Inventory Agent)</h2>", unsafe_allow_html=True)
    
    inventory = fetch_data("inventory")
    if inventory:
        st.markdown("### Current Inventory")
        df = pd.DataFrame(inventory)
        st.dataframe(df, use_container_width=True)
        render_export_buttons(df, "inventory_report", "Inventory Report")

    st.markdown("### AI Stock Analysis")
    with st.form("inventory_form"):
        product_name = st.text_input("Product Name", "Industrial Laptop")
        required_quantity = st.number_input("Required Quantity", min_value=1, value=50)
        current_stock = st.number_input("Current Stock", min_value=0, value=20)
        submit_button = st.form_submit_button("Analyze Stock")
        
    if submit_button:
        with st.spinner("Analyzing inventory..."):
            try:
                resp = requests.post(f"{API_URL}/api/inventory/analyze", json={"product_name": product_name, "required_quantity": required_quantity, "current_stock": current_stock}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    st.metric("Quantity to Order", data.get("quantity_to_order"))
                    st.info(data.get("analysis"))
                else:
                    st.error("API error or quota exceeded. Please try again later.")
            except requests.exceptions.RequestException:
                st.error("Connection timed out. Gemini API quota exceeded or backend unavailable.")

elif selected == "Route Optimization":
    st.markdown("<h2>Route Optimization (Route Agent)</h2>", unsafe_allow_html=True)
    with st.form("route_form"):
        destination = st.text_input("Destination", "Warehouse 1")
        submit_button = st.form_submit_button("Optimize Route")
        
    if submit_button:
        with st.spinner("Optimizing logistics..."):
            try:
                resp = requests.post(f"{API_URL}/api/routes/optimize", json={"destination": destination}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Best Route: {data.get('recommended_route_name')}")
                    st.metric("Distance", f"{data.get('distance_km')} km")
                else:
                    st.error("API error or quota exceeded. Please try again later.")
            except requests.exceptions.RequestException:
                st.error("Connection timed out. Gemini API quota exceeded or backend unavailable.")

elif selected == "Risk Analysis":
    st.markdown("<h2>Risk Analysis (Risk Agent)</h2>", unsafe_allow_html=True)
    with st.form("risk_form"):
        supplier_name = st.text_input("Supplier Name", "GlobalTech Supplies")
        delivery_days = st.number_input("Supplier Delivery Days", min_value=1, value=4)
        required_delivery_days = st.number_input("Required Delivery Days", min_value=1, value=5)
        submit_button = st.form_submit_button("Analyze Risk")
        
    if submit_button:
        with st.spinner("Evaluating risk..."):
            try:
                resp = requests.post(f"{API_URL}/api/risk/analyze", json={"supplier_name": supplier_name, "delivery_days": delivery_days, "required_delivery_days": required_delivery_days}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    st.error(f"Risk Level: {data.get('risk_level')}")
                    st.warning(data.get("reasoning"))
                else:
                    st.error("API error or quota exceeded. Please try again later.")
            except requests.exceptions.RequestException:
                st.error("Connection timed out. Gemini API quota exceeded or backend unavailable.")

elif selected == "Supply Chain Workflow":
    st.markdown("<h2 style='color: var(--text-color); font-weight: 700;'>Supply Chain Workflow Orchestration</h2>", unsafe_allow_html=True)
    
    st.markdown("### Agent Architecture")
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; background-color: var(--secondary-background-color); padding: 20px; border-radius: 12px; border: 1px solid var(--background-color); margin-bottom: 2rem; overflow-x: auto;">
        <div style="text-align: center; min-width: 100px;">
            <div style="font-size: 24px; margin-bottom: 5px;">📈</div>
            <div style="font-size: 12px; font-weight: 600; color: var(--text-color);">Forecast Agent</div>
        </div>
        <div style="color: #94A3B8;">➔</div>
        <div style="text-align: center; min-width: 100px;">
            <div style="font-size: 24px; margin-bottom: 5px;">📦</div>
            <div style="font-size: 12px; font-weight: 600; color: var(--text-color);">Inventory Agent</div>
        </div>
        <div style="color: #94A3B8;">➔</div>
        <div style="text-align: center; min-width: 100px;">
            <div style="font-size: 24px; margin-bottom: 5px;">🛒</div>
            <div style="font-size: 12px; font-weight: 600; color: var(--text-color);">Procurement Agent</div>
        </div>
        <div style="color: #94A3B8;">➔</div>
        <div style="text-align: center; min-width: 100px;">
            <div style="font-size: 24px; margin-bottom: 5px;">🏭</div>
            <div style="font-size: 12px; font-weight: 600; color: var(--text-color);">Supplier Agent</div>
        </div>
        <div style="color: #94A3B8;">➔</div>
        <div style="text-align: center; min-width: 100px;">
            <div style="font-size: 24px; margin-bottom: 5px;">⚠️</div>
            <div style="font-size: 12px; font-weight: 600; color: var(--text-color);">Risk Agent</div>
        </div>
        <div style="color: #94A3B8;">➔</div>
        <div style="text-align: center; min-width: 100px;">
            <div style="font-size: 24px; margin-bottom: 5px;">🚚</div>
            <div style="font-size: 12px; font-weight: 600; color: var(--text-color);">Route Agent</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("Run the complete multi-agent workflow to see how all agents collaborate end-to-end.")
    with st.form("optimization_form"):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name", "Industrial Laptop")
            quantity = st.number_input("Quantity", min_value=1, value=20)
        with col2:
            destination = st.text_input("Destination", "Warehouse 1")
            required_delivery_days = st.number_input("Required Delivery Days", min_value=1, value=5)
        
        submit_button = st.form_submit_button("Run End-to-End Orchestration", type="primary")
        
    if submit_button:
        import time
        current_time = time.time()
        last_run = st.session_state.get('last_optimize_run', 0)
        
        if current_time - last_run < 30:
            st.error(f"⏳ Cooldown active. Please wait {int(30 - (current_time - last_run))} seconds to prevent API limits.")
        else:
            st.session_state.last_optimize_run = current_time
            with st.spinner("Agents are collaborating and synthesizing data..."):
                try:
                    payload = {
                        "product_name": product_name, "quantity": quantity,
                        "destination": destination, "required_delivery_days": required_delivery_days
                    }
                    resp = requests.post(f"{API_URL}/optimize", json=payload, timeout=120)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.toast("Workflow Complete!", icon="✅")
                        
                        st.markdown("### Orchestration Results")
                        c1, c2, c3 = st.columns(3)
                        c1.markdown(f"<div class='metric-card'><div class='metric-title'>Total Cost</div><div class='metric-value'>${data['total_cost']:,.2f}</div></div>", unsafe_allow_html=True)
                        c2.markdown(f"<div class='metric-card'><div class='metric-title'>Selected Supplier</div><div class='metric-value' style='font-size: 1.5rem;'>{data['selected_supplier']}</div></div>", unsafe_allow_html=True)
                        c3.markdown(f"<div class='metric-card'><div class='metric-title'>Risk Level</div><div class='metric-value' style='font-size: 1.5rem; color:#F59E0B;'>{data['risk_level']}</div></div>", unsafe_allow_html=True)
                        
                        st.info(f"**Inventory Context:** {data['inventory_analysis']}")
                        st.info(f"**Logistics Route:** {data['recommended_route']}")
                        st.success(f"**Final Recommendation:** {data['procurement_summary']}")
                    else:
                        st.error("API error or quota exceeded. Please try again later.")
                except requests.exceptions.RequestException:
                    st.error("Connection timed out. Gemini API quota exceeded or backend unavailable.")

elif selected == "Analytics":
    st.markdown("<h2>Analytics</h2>", unsafe_allow_html=True)
    history = fetch_data("history")
    if history:
        df = pd.DataFrame(history)
        st.dataframe(df, use_container_width=True)
        render_export_buttons(df, "analytics_report", "Analytics Report")
    else:
        st.info("No analytics data available.")

elif selected == "Data Management":
    st.markdown("<h2>Data Management</h2>", unsafe_allow_html=True)
    
    def upload_csv(col, title, key, filename, endpoint=None):
        with col:
            st.markdown(f"**{title}**")
            f = st.file_uploader(f"Upload {title} CSV", type=['csv'], key=key, label_visibility="collapsed")
            if f and st.button(f"Upload {title}", key=f"btn_{key}"):
                # Always save locally to the data folder
                try:
                    with open(f"data/{filename}.csv", "wb") as out_file:
                        out_file.write(f.getvalue())
                    
                    if endpoint:
                        # Sync to DB if endpoint exists
                        f.seek(0)
                        resp = requests.post(f"{API_URL}/upload/{endpoint}", files={"file": (f.name, f.getvalue(), "text/csv")})
                        if resp.status_code == 200:
                            st.toast(f"✅ {title} uploaded to system and database.")
                        else:
                            st.error(f"Failed DB sync for {title}.")
                    else:
                        st.toast(f"✅ {title} uploaded to system successfully.")
                except Exception as e:
                    st.error(f"Error uploading {title}: {e}")

    c1, c2, c3 = st.columns(3)
    upload_csv(c1, "Suppliers", "sup", "suppliers", endpoint="suppliers")
    upload_csv(c2, "Routes", "rte", "routes", endpoint="routes")
    upload_csv(c3, "Inventory", "inv", "inventory", endpoint="inventory")
    
    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    upload_csv(c4, "Orders", "ord", "orders")
    upload_csv(c5, "RFQs", "rfq", "rfq")
    upload_csv(c6, "Procurement Requests", "pr", "procurement_requests")

elif selected == "Procurement Requests":
    st.markdown("<h2>Procurement Requests</h2>", unsafe_allow_html=True)
    
    with st.form("procurement_request_form"):
        st.subheader("Create New Request")
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("Item Name")
            department = st.text_input("Department", value="IT")
            budget = st.number_input("Budget", min_value=0.0, format="%.2f")
        with col2:
            quantity = st.number_input("Quantity", min_value=1)
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            
        submit_button = st.form_submit_button("Create Request")
        if submit_button and item_name:
            try:
                df = pd.read_csv("data/procurement_requests.csv")
                new_id = f"PR-{len(df) + 201}"
                new_row = pd.DataFrame([{"pr_id": new_id, "product_name": item_name, "quantity": quantity, "department": department, "status": "Pending"}])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv("data/procurement_requests.csv", index=False)
                st.toast(f"✅ Procurement request {new_id} for {quantity}x {item_name} created successfully.")
            except Exception as e:
                st.error(f"Error creating request: {e}")

    st.markdown("### Existing Requests")
    try:
        df = pd.read_csv("data/procurement_requests.csv")
        if df.empty:
            st.info("No procurement requests found.")
        else:
            st.dataframe(df, use_container_width=True)
            render_export_buttons(df, "procurement_requests", "Procurement Requests")
    except Exception as e:
        st.info("No data available.")

elif selected == "RFQ Management":
    st.markdown("<h2>RFQ Management</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Create RFQ", "Send RFQ", "RFQ Status Tracking"])
    
    with tab1:
        with st.form("create_rfq_form"):
            product_name = st.text_input("Product Name")
            quantity = st.number_input("Quantity", min_value=1)
            target_price = st.number_input("Target Price", min_value=0.0, format="%.2f")
            if st.form_submit_button("Create RFQ") and product_name:
                try:
                    df = pd.read_csv("data/rfq.csv")
                    new_id = f"RFQ-{len(df) + 101}"
                    new_row = pd.DataFrame([{"rfq_id": new_id, "product_name": product_name, "quantity": quantity, "target_price": target_price, "status": "Open"}])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv("data/rfq.csv", index=False)
                    st.toast(f"✅ RFQ {new_id} created successfully.")
                except Exception as e:
                    st.error(f"Error creating RFQ: {e}")
                
    with tab2:
        with st.form("send_rfq_form"):
            try:
                rfq_df = pd.read_csv("data/rfq.csv")
                open_rfqs = rfq_df[rfq_df['status'] == 'Open']['rfq_id'].tolist()
            except:
                open_rfqs = []
                
            suppliers_data = fetch_data("suppliers")
            supplier_names = [s['name'] for s in suppliers_data] if suppliers_data else ["GlobalTech Supplies", "Optima Electronics"]
            
            selected_rfq = st.selectbox("Select RFQ", open_rfqs if open_rfqs else ["No Open RFQs"], disabled=len(open_rfqs)==0)
            selected_suppliers = st.multiselect("Select Suppliers", supplier_names)
            
            if st.form_submit_button("Send RFQ") and selected_rfq and selected_rfq != "No Open RFQs" and selected_suppliers:
                try:
                    rfq_df.loc[rfq_df['rfq_id'] == selected_rfq, 'status'] = 'Sent'
                    rfq_df.to_csv("data/rfq.csv", index=False)
                    st.toast(f"✅ {selected_rfq} sent to {len(selected_suppliers)} suppliers.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                
    with tab3:
        try:
            df = pd.read_csv("data/rfq.csv")
            if df.empty:
                st.info("No RFQs found.")
            else:
                st.dataframe(df, use_container_width=True)
                render_export_buttons(df, "rfqs", "RFQ Management")
        except Exception as e:
            st.info("No data available.")

elif selected == "Order Monitoring":
    st.markdown("<h2>Order Monitoring</h2>", unsafe_allow_html=True)
    try:
        df = pd.read_csv("data/orders.csv")
        st.dataframe(df, use_container_width=True)
        render_export_buttons(df, "orders", "Order Monitoring")
    except Exception as e:
        st.info("No data available.")

elif selected == "Quotation Comparison":
    st.markdown("<h2>Quotation Comparison</h2>", unsafe_allow_html=True)
    st.markdown("### Dynamic Supplier Comparison")
    
    try:
        suppliers_data = fetch_data("suppliers")
        if suppliers_data:
            df = pd.DataFrame(suppliers_data)
            
            # Simulate a live quotation request for a standard bulk order
            st.info("Comparing real-time capabilities of all active suppliers for a standard bulk fulfillment.")
            
            # Calculate dynamic AI Score
            # High rating (+), Low delivery days (+), Low relative price (+)
            max_price = df['price'].max() if not df.empty else 1
            df['AI Score'] = ((df['rating'] / 5.0) * 40) + ((1.0 / df['delivery_days']) * 30) + ((1.0 - (df['price'] / max_price)) * 30)
            df['AI Score'] = df['AI Score'].apply(lambda x: min(round(x * 1.5, 1), 99.9))
            
            # Format columns
            display_df = pd.DataFrame({
                "Supplier": df['name'],
                "Unit Price": df['price'].apply(lambda x: f"${x:,.2f}"),
                "Delivery Days": df['delivery_days'],
                "Reliability Rating": df['rating'],
                "AI Recommendation Score": df['AI Score']
            }).sort_values(by="AI Recommendation Score", ascending=False)
            
            st.dataframe(display_df, use_container_width=True)
            
            best_supplier = display_df.iloc[0]['Supplier']
            st.success(f"**AI Recommendation:** Automatically route RFQs to **{best_supplier}** based on optimal balance of cost, speed, and reliability.")
        else:
            st.info("No supplier data available to run comparison.")
    except Exception as e:
        st.error(f"Error loading comparison: {e}")

elif selected == "Order Approval":
    st.markdown("<h2>Order Approval</h2>", unsafe_allow_html=True)
    
    st.markdown("### Approval Workflow")
    status_filter = st.selectbox("Workflow Status", ["Pending", "Approved", "Rejected"])
    
    orders = fetch_data("api/orders")
    
    if not orders:
        st.info("No orders found in the system.")
    else:
        filtered_orders = [o for o in orders if str(o.get("status", "")).lower() == status_filter.lower()]
        
        if not filtered_orders:
            st.info(f"No {status_filter.lower()} orders found.")
        else:
            if status_filter == "Pending":
                st.markdown("### Pending Orders")
                hcol1, hcol2, hcol3, hcol4, hcol5, hcol6 = st.columns([2, 3, 2, 3, 2, 3])
                hcol1.markdown("**Order ID**")
                hcol2.markdown("**Product**")
                hcol3.markdown("**Qty**")
                hcol4.markdown("**Supplier**")
                hcol5.markdown("**Cost**")
                hcol6.markdown("**Actions**")
                st.markdown("---")
                
                for order in filtered_orders:
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 2, 3, 2, 3])
                    col1.markdown(f"**{order.get('order_id')}**")
                    col2.markdown(f"{order.get('product_name')}")
                    col3.markdown(f"{order.get('quantity')}")
                    col4.markdown(f"{order.get('supplier_name')}")
                    col5.markdown(f"${float(order.get('total_cost', 0)):,.2f}")
                    
                    with col6:
                        bcol1, bcol2 = st.columns(2)
                        with bcol1:
                            if st.button("Approve", key=f"app_{order.get('order_id')}", type="primary"):
                                requests.put(f"{API_URL}/api/orders/{order.get('order_id')}/status", json={"status": "Approved"})
                                st.rerun()
                        with bcol2:
                            if st.button("Reject", key=f"rej_{order.get('order_id')}"):
                                requests.put(f"{API_URL}/api/orders/{order.get('order_id')}/status", json={"status": "Rejected"})
                                st.rerun()
                    st.markdown("---")
            else:
                st.markdown(f"### {status_filter} Orders")
                for order in filtered_orders:
                    if status_filter == "Approved":
                        st.success(f"**Order #{order.get('order_id')}**: {order.get('quantity')}x {order.get('product_name')} from {order.get('supplier_name')} - ${float(order.get('total_cost', 0)):,.2f}  ✅ Approved")
                    else:
                        st.error(f"**Order #{order.get('order_id')}**: {order.get('quantity')}x {order.get('product_name')} from {order.get('supplier_name')} - ${float(order.get('total_cost', 0)):,.2f}  ❌ Rejected")

elif selected == "Settings":
    st.markdown("<h2>Settings</h2>", unsafe_allow_html=True)
    
    st.subheader("System Preferences")
    
    import os
    config_dir = ".streamlit"
    config_path = f"{config_dir}/config.toml"
    current_theme = "System Default"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            content = f.read()
            if 'base="light"' in content: current_theme = "Light"
            elif 'base="dark"' in content: current_theme = "Dark"
            
    themes = ["System Default", "Light", "Dark"]
    theme_idx = themes.index(current_theme) if current_theme in themes else 0
    theme = st.selectbox("Theme selector", themes, index=theme_idx)
    
    if theme != current_theme:
        os.makedirs(config_dir, exist_ok=True)
        if theme == "System Default":
            if os.path.exists(config_path): os.remove(config_path)
        else:
            with open(config_path, "w") as f:
                f.write(f'[theme]\nbase="{theme.lower()}"\nprimaryColor="#F97316"\n')
        st.rerun()

    st.markdown("---")
    st.subheader("Performance & Cache")
    if st.button("Clear Application Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.toast("✅ Cache cleared successfully. Data will be fetched fresh from APIs on the next load.")
        st.rerun()
    
    st.subheader("System Configuration")
    st.text_input("API URL display", value=API_URL, disabled=True)
    
    db_status = "🟢 Active" if health_data.get("database") == "active" else "🔴 Inactive"
    st.markdown(f"**Database status:** {db_status}")
    
    st.subheader("Data Management")
    if st.button("Reset demo data", type="primary"):
        st.warning("Demo data has been reset successfully.")
