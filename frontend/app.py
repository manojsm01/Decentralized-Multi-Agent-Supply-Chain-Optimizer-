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


# Initialize session state for navigation and auth
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "Home"
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user' not in st.session_state:
    st.session_state.user = None

# ----------------- AUTHENTICATION -----------------
def login(username, password):
    try:
        resp = requests.post(f"{API_URL}/api/auth/login", data={"username": username, "password": password})
        if resp.status_code == 200:
            token_data = resp.json()
            st.session_state.access_token = token_data['access_token']
            
            user_resp = requests.get(f"{API_URL}/api/users/me", headers={"Authorization": f"Bearer {st.session_state.access_token}"})
            if user_resp.status_code == 200:
                st.session_state.user = user_resp.json()
            return True
        return False
    except Exception as e:
        return False

def logout():
    st.session_state.access_token = None
    st.session_state.user = None
    st.rerun()

def get_auth_headers():
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}

if not st.session_state.access_token:
    st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/2830/2830305.png' width='80'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; padding-top: 4rem;'>Welcome to Supply Chain Optimizer</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            if submit:
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password, or API is offline.")
    st.stop()
# --------------------------------------------------


# 2. CUSTOM CSS - Enterprise Theme
st.markdown("""
<style>
/* Glassmorphism Theme */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    color: #FFFFFF;
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0B1220 0%, #131C31 100%);
}
[data-testid="stHeader"] {
    background-color: transparent;
}
[data-testid="stSidebar"] {
    background-color: rgba(19, 28, 49, 0.6) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.15);
    padding-top: 1rem;
}
.custom-header {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.15);
    color: white;
    padding: 2.5rem 2rem;
    border-radius: 24px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px -5px rgba(0,0,0,0.5);
}
.custom-header h1 {
    color: white;
    margin: 0;
    font-size: 2.2rem;
    font-weight: 700;
}
.custom-header p {
    color: #BFC7D5;
    font-size: 1.1rem;
    margin-top: 0.5rem;
}
.metric-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    padding: 1.5rem;
    border-radius: 18px;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.15);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 35px -5px rgba(0,0,0,0.5);
    border: 1px solid rgba(255,255,255,0.25);
}
.metric-title {
    color: #BFC7D5;
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
.metric-value {
    color: #FFFFFF;
    font-size: 2.2rem;
    font-weight: 700;
}
.metric-change.positive { color: #22C55E; }
.metric-change.negative { color: #EF4444; }
[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 18px;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    padding: 1rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.15);
}
.stButton>button {
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
}
.stButton>button[kind="primary"] {
    background: linear-gradient(135deg, #00D4FF 0%, #0077FF 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# Cache API requests to avoid redundant calls
def fetch_data(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}", headers=get_auth_headers())
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
    st.markdown("<div style='text-align:center; padding-bottom: 1rem;'><img src='https://cdn-icons-png.flaticon.com/512/2830/2830305.png' width='50'></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; padding-bottom: 1rem;'><h2 style='color: var(--text-color); font-weight: 700; margin-bottom: 0;'>Supply Chain Optimizer</h2><span style='color: var(--text-color); font-size: 0.8rem;'>Enterprise Edition</span></div>", unsafe_allow_html=True)
    
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
        "⚙️ Settings",
        "🛡️ Admin Panel"
    ]

    if st.session_state.user.get('role') != 'admin':
        if "🛡️ Admin Panel" in options:
            options.remove("🛡️ Admin Panel")

    
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
        "⚙️ Settings": "Settings",
        "🛡️ Admin Panel": "Admin Panel"
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
    st.markdown(f"<div style='font-size:0.8rem; font-weight:600; color: var(--text-color);'>Logged in as: {st.session_state.user['username']} ({st.session_state.user['role']})</div>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        logout()

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

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("<h2 style='color: var(--text-color); font-weight: 700; margin: 0; padding: 0.5rem 0 2rem 0;'>Command Center</h2>", unsafe_allow_html=True)
    with col2:
        st.write("") # Spacer
        summary_df = pd.DataFrame([{"Metric": "Total Spend", "Value": f"${total_spend:,.2f}"}, {"Metric": "Total Orders", "Value": total_orders}, {"Metric": "Active Suppliers", "Value": active_suppliers}, {"Metric": "Low Stock Items", "Value": low_stock_items}])
        st.download_button(label="📥 Export Report", data=summary_df.to_csv(index=False), file_name="dashboard_summary.csv", mime="text/csv", use_container_width=True)
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

    st.markdown("<h3 style='color: var(--text-color); margin-top: 2rem; margin-bottom: 1rem;'>Advanced Analytics</h3>", unsafe_allow_html=True)
    adv1, adv2 = st.columns([1, 1])
    
    with adv1:
        if suppliers:
            df_sup = pd.DataFrame(suppliers)
            fig_bubble = go.Figure(go.Scatter(
                x=df_sup['delivery_days'], y=df_sup['price'],
                mode='markers',
                marker=dict(size=df_sup['rating']*10, color='#00D4FF', opacity=0.7, line=dict(width=1, color='#FFFFFF')),
                text=df_sup['name'],
                hovertemplate="<b>%{text}</b><br>Delivery: %{x} days<br>Price: $%{y}<br>Rating: %{marker.size}<extra></extra>"
            ))
            fig_bubble.update_layout(title=dict(text="Supplier Efficiency Matrix", font=dict(size=16, color=None, family="Inter")),
                                     xaxis_title="Delivery Days", yaxis_title="Price ($)",
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=60, b=40), height=400, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'))
            st.plotly_chart(fig_bubble, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No supplier data for matrix.")
            
    with adv2:
        if inventory:
            df_inv_full = pd.DataFrame(inventory).sort_values(by='stock_level', ascending=True)
            colors_inv = ['#EF4444' if int(v) < 50 else '#F59E0B' if int(v) < 150 else '#10B981' for v in df_inv_full['stock_level']]
            fig_inv_risk = go.Figure(go.Bar(x=df_inv_full['product_name'], y=df_inv_full['stock_level'], marker_color=colors_inv))
            fig_inv_risk.update_layout(title=dict(text="Inventory Risk Assessment", font=dict(size=16, color=None, family="Inter")),
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=60, b=40), height=400, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'))
            st.plotly_chart(fig_inv_risk, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No inventory data for risk assessment.")
            
    if not df_orders.empty and suppliers:
        st.markdown("<h4 style='color: var(--text-color); margin-top: 1rem; margin-bottom: 1rem;'>Procurement Capital Flow</h4>", unsafe_allow_html=True)
        products = list(df_orders['product_name'].unique()) if 'product_name' in df_orders.columns else []
        if products:
            supplier_names = list(df_orders['supplier_name'].unique())
            statuses = list(df_orders['status'].unique())
            
            nodes = products + supplier_names + statuses
            node_indices = {name: i for i, name in enumerate(nodes)}
            
            sources = []
            targets = []
            values = []
            
            for _, row in df_orders.iterrows():
                sources.append(node_indices[row['product_name']])
                targets.append(node_indices[row['supplier_name']])
                values.append(row['total_cost'])
                
                sources.append(node_indices[row['supplier_name']])
                targets.append(node_indices[row['status']])
                values.append(row['total_cost'])
                
            fig_sankey = go.Figure(data=[go.Sankey(
                node = dict(pad=15, thickness=20, line=dict(color="rgba(255,255,255,0.2)", width=0.5), label=nodes, color="#00D4FF"),
                link = dict(source=sources, target=targets, value=values, color="rgba(0, 212, 255, 0.3)")
            )])
            fig_sankey.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), height=400, font=dict(color="#FFFFFF"))
            st.plotly_chart(fig_sankey, use_container_width=True, config={'displayModeBar': False})

elif selected == "Demand Forecasting":
    st.markdown("<h2>Demand Forecasting (Forecast Agent)</h2>", unsafe_allow_html=True)
    with st.form("forecast_form"):
        product_name = st.text_input("Product Name", "Industrial Laptop")
        quantity = st.number_input("Requested Quantity", min_value=1, value=100)
        submit_button = st.form_submit_button("Run Forecast Analysis")
        
    if submit_button:
        with st.spinner("Analyzing demand trends..."):
            try:
                resp = requests.post(f"{API_URL}/api/forecast", json={"product_name": product_name, "quantity": quantity}, timeout=90, headers=get_auth_headers())
                if resp.status_code == 200:
                    data = resp.json()
                    st.success("Analysis Complete")
                    st.metric("Recommended Quantity to Order", data.get("quantity_to_order"))
                    st.info(data.get("analysis"))
                else:
                    st.error("API error or quota exceeded. Please try again later.")
            except requests.exceptions.RequestException:
                st.error("Connection timed out. NVIDIA API quota exceeded or backend unavailable.")

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
                resp = requests.post(f"{API_URL}/api/suppliers/recommend", json={"required_delivery_days": required_delivery_days}, timeout=90, headers=get_auth_headers())
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
                st.error("Connection timed out. NVIDIA API quota exceeded or backend unavailable.")

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
                resp = requests.post(f"{API_URL}/api/inventory/analyze", json={"product_name": product_name, "required_quantity": required_quantity, "current_stock": current_stock}, timeout=90, headers=get_auth_headers())
                if resp.status_code == 200:
                    data = resp.json()
                    st.metric("Quantity to Order", data.get("quantity_to_order"))
                    st.info(data.get("analysis"))
                else:
                    st.error("API error or quota exceeded. Please try again later.")
            except requests.exceptions.RequestException:
                st.error("Connection timed out. NVIDIA API quota exceeded or backend unavailable.")

elif selected == "Route Optimization":
    st.markdown("<h2>Route Optimization (Route Agent)</h2>", unsafe_allow_html=True)
    with st.form("route_form"):
        destination = st.text_input("Destination", "Warehouse 1")
        submit_button = st.form_submit_button("Optimize Route")
        
    if submit_button:
        with st.spinner("Optimizing logistics..."):
            try:
                resp = requests.post(f"{API_URL}/api/routes/optimize", json={"destination": destination}, timeout=90, headers=get_auth_headers())
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Best Route: {data.get('recommended_route_name')}")
                    st.metric("Distance", f"{data.get('distance_km')} km")
                else:
                    st.error("API error or quota exceeded. Please try again later.")
            except requests.exceptions.RequestException:
                st.error("Connection timed out. NVIDIA API quota exceeded or backend unavailable.")

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
                resp = requests.post(f"{API_URL}/api/risk/analyze", json={"supplier_name": supplier_name, "delivery_days": delivery_days, "required_delivery_days": required_delivery_days}, timeout=90, headers=get_auth_headers())
                if resp.status_code == 200:
                    data = resp.json()
                    st.error(f"Risk Level: {data.get('risk_level')}")
                    st.warning(data.get("reasoning"))
                else:
                    st.error("API error or quota exceeded. Please try again later.")
            except requests.exceptions.RequestException:
                st.error("Connection timed out. NVIDIA API quota exceeded or backend unavailable.")

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
                    resp = requests.post(f"{API_URL}/optimize", json=payload, timeout=120, headers=get_auth_headers())
                    if resp.status_code == 200:
                        data = resp.json()
                        st.toast("Workflow Complete!", icon="✅")
                        
                        st.markdown("### Orchestration Results")
                        c1, c2, c3 = st.columns(3)
                        c1.markdown(f"<div class='metric-card'><div class='metric-title'>Total Cost</div><div class='metric-value'>${data['total_cost']:,.2f}</div></div>", unsafe_allow_html=True)
                        c2.markdown(f"<div class='metric-card'><div class='metric-title'>Selected Supplier</div><div class='metric-value' style='font-size: 1.5rem;'>{data['selected_supplier']}</div></div>", unsafe_allow_html=True)
                        c3.markdown(f"<div class='metric-card'><div class='metric-title'>Risk Level</div><div class='metric-value' style='font-size: 1.5rem; color:#F59E0B;'>{data['risk_level']}</div></div>", unsafe_allow_html=True)
                        
                        inv_analysis = str(data.get('inventory_analysis', '')).replace('$', '\\$')
                        rec_route = str(data.get('recommended_route', '')).replace('$', '\\$')
                        proc_summary = str(data.get('procurement_summary', '')).replace('$', '\\$')
                        
                        st.info(f"**Inventory Context:** {inv_analysis}")
                        st.info(f"**Logistics Route:** {rec_route}")
                        st.success(f"**Final Recommendation:** {proc_summary}")
                    else:
                        st.error("API error or quota exceeded. Please try again later.")
                except requests.exceptions.RequestException:
                    st.error("Connection timed out. NVIDIA API quota exceeded or backend unavailable.")

elif selected == "Analytics":
    st.markdown("<h2>Analytics Dashboard</h2>", unsafe_allow_html=True)
    history = fetch_data("history")
    if history:
        df = pd.DataFrame(history)
        
        # Key Metrics
        st.markdown("### Key Performance Indicators")
        kpi1, kpi2, kpi3 = st.columns(3)
        total_spend = df['total_cost'].sum() if 'total_cost' in df.columns else 0
        total_orders = len(df)
        avg_order_value = total_spend / total_orders if total_orders > 0 else 0
        
        kpi1.markdown(f"<div class='metric-card'><div class='metric-title'>Total Spend</div><div class='metric-value'>${total_spend:,.2f}</div></div>", unsafe_allow_html=True)
        kpi2.markdown(f"<div class='metric-card'><div class='metric-title'>Total Transactions</div><div class='metric-value'>{total_orders}</div></div>", unsafe_allow_html=True)
        kpi3.markdown(f"<div class='metric-card'><div class='metric-title'>Avg Order Value</div><div class='metric-value'>${avg_order_value:,.2f}</div></div>", unsafe_allow_html=True)
        
        # Charts
        import plotly.express as px
        st.markdown("### Spend Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'selected_supplier' in df.columns and 'total_cost' in df.columns:
                spend_by_supplier = df.groupby('selected_supplier')['total_cost'].sum().reset_index()
                fig1 = px.pie(spend_by_supplier, values='total_cost', names='selected_supplier', title='Spend Distribution by Supplier', hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
                fig1.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig1, use_container_width=True)
                
        with col2:
            if 'product_name' in df.columns and 'total_cost' in df.columns:
                spend_by_product = df.groupby('product_name')['total_cost'].sum().reset_index().sort_values(by='total_cost', ascending=False)
                fig2 = px.bar(spend_by_product, x='product_name', y='total_cost', title='Total Spend by Product', color='total_cost', color_continuous_scale='Teal')
                fig2.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("### Raw Data")
        st.dataframe(df, use_container_width=True)
        render_export_buttons(df, "analytics_report", "Analytics Report")
    else:
        st.info("No analytics data available. Run some workflows to generate data!")


elif selected == "Admin Panel":
    st.markdown("<h2>Admin Panel</h2>", unsafe_allow_html=True)
    
    if st.session_state.user['role'] != 'admin':
        st.error("Access Denied. You must be an administrator to view this page.")
    else:
        st.markdown("### Create New User")
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
            new_org = st.text_input("Organization (Optional)")
            submit = st.form_submit_button("Create User")
            
            if submit and new_username and new_password:
                try:
                    resp = requests.post(f"{API_URL}/api/admin/users", 
                        json={"username": new_username, "password": new_password, "role": new_role, "organization": new_org},
                        headers=get_auth_headers()
                    )
                    if resp.status_code == 200:
                        st.success(f"User '{new_username}' created successfully!")
                    else:
                        st.error(f"Error creating user: {resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

        st.divider()
        st.subheader("👥 Manage Existing Users")
        users_resp = requests.get(f"{API_URL}/api/admin/users", headers=get_auth_headers())
        if users_resp.status_code == 200:
            users = users_resp.json()
            if users:
                user_df = pd.DataFrame(users)
                st.dataframe(user_df[['id', 'username', 'role', 'organization']], hide_index=True)
                
                st.write("#### Edit / Delete User")
                selected_user = st.selectbox("Select User to Manage", [u['username'] for u in users])
                if selected_user:
                    user_data = next(u for u in users if u['username'] == selected_user)
                    with st.form("edit_user_form"):
                        new_role = st.selectbox("Role", ["user", "admin"], index=0 if user_data['role']=='user' else 1)
                        new_org = st.text_input("Organization", value=user_data['organization'] or "")
                        
                        col1, col2 = st.columns(2)
                        update_btn = col1.form_submit_button("Update User")
                        delete_btn = col2.form_submit_button("Delete User", type="primary")
                        
                        if update_btn:
                            res = requests.put(f"{API_URL}/api/admin/users/{selected_user}", json={"role": new_role, "organization": new_org}, headers=get_auth_headers())
                            if res.status_code == 200:
                                st.success(f"User {selected_user} updated!")
                                st.rerun()
                            else:
                                st.error(res.text)
                                
                        if delete_btn:
                            if selected_user == "admin":
                                st.error("Cannot delete root admin.")
                            else:
                                res = requests.delete(f"{API_URL}/api/admin/users/{selected_user}", headers=get_auth_headers())
                                if res.status_code == 200:
                                    st.success(f"User {selected_user} deleted!")
                                    st.rerun()
                                else:
                                    st.error(res.text)
                    


elif selected == "Data Management":
    st.markdown("<h2>Data Management</h2>", unsafe_allow_html=True)
    
    def upload_csv(col, title, key, filename, endpoint=None):
        with col:
            st.markdown(f"**{title}**")
            f = st.file_uploader(f"Upload {title} CSV", type=['csv'], key=key, label_visibility="collapsed")
            if f and st.button(f"Upload {title}", key=f"btn_{key}"):
                # Always save locally to the data folder
                try:
                    org = st.session_state.user.get('organization', 'System')
                    os.makedirs(f"data/{org}", exist_ok=True)
                    with open(f"data/{org}/{filename}.csv", "wb") as out_file:
                        out_file.write(f.getvalue())
                    
                    if endpoint:
                        # Sync to DB if endpoint exists
                        f.seek(0)
                        resp = requests.post(f"{API_URL}/upload/{endpoint}", files={"file": (f.name, f.getvalue(), "text/csv")}, headers=get_auth_headers())
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
                org = st.session_state.user.get('organization', 'System')
                os.makedirs(f"data/{org}", exist_ok=True)
                df = pd.read_csv(f"data/{org}/procurement_requests.csv")
                new_id = f"PR-{len(df) + 201}"
                new_row = pd.DataFrame([{"pr_id": new_id, "product_name": item_name, "quantity": quantity, "department": department, "status": "Pending"}])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(f"data/{org}/procurement_requests.csv", index=False)
                
                # Automatically create a corresponding Pending Order for the Order Approval tab
                order_payload = {
                    "order_id": new_id.replace("PR-", "ORD-"),
                    "product_name": item_name,
                    "quantity": quantity,
                    "supplier_name": "TBD (Pending Sourcing)",
                    "total_cost": budget,
                    "status": "Pending",
                    "date": __import__('datetime').datetime.now().strftime("%Y-%m-%d")
                }
                requests.post(f"{API_URL}/api/orders", json=order_payload, headers=get_auth_headers())
                
                st.toast(f"✅ Procurement request {new_id} for {quantity}x {item_name} created successfully.")
            except Exception as e:
                st.error(f"Error creating request: {e}")

    st.markdown("### Existing Requests")
    try:
        org = st.session_state.user.get('organization', 'System')
        df = pd.read_csv(f"data/{org}/procurement_requests.csv")
        if df.empty:
            st.info("No procurement requests found.", headers=get_auth_headers())
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
                    org = st.session_state.user.get('organization', 'System')
                    os.makedirs(f"data/{org}", exist_ok=True)
                    df = pd.read_csv(f"data/{org}/rfq.csv")
                    new_id = f"RFQ-{len(df) + 101}"
                    new_row = pd.DataFrame([{"rfq_id": new_id, "product_name": product_name, "quantity": quantity, "target_price": target_price, "status": "Open"}])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(f"data/{org}/rfq.csv", index=False)
                    st.toast(f"✅ RFQ {new_id} created successfully.")
                except Exception as e:
                    st.error(f"Error creating RFQ: {e}")
                
    with tab2:
        with st.form("send_rfq_form"):
            try:
                org = st.session_state.user.get('organization', 'System')
                rfq_df = pd.read_csv(f"data/{org}/rfq.csv")
                open_rfqs = rfq_df[rfq_df['status'] == 'Open']['rfq_id'].tolist()
            except:
                open_rfqs = []
                
            suppliers_data = fetch_data("suppliers")
            supplier_names = [s['name'] for s in suppliers_data] if suppliers_data else ["GlobalTech Supplies", "Optima Electronics"]
            
            selected_rfq = st.selectbox("Select RFQ", open_rfqs if open_rfqs else ["No Open RFQs"], disabled=len(open_rfqs)==0)
            selected_suppliers = st.multiselect("Select Suppliers", supplier_names)
            
            submit_rfq = st.form_submit_button("Send RFQ")
            if submit_rfq:
                if not selected_rfq or selected_rfq == "No Open RFQs":
                    st.error("No valid RFQ selected.")
                elif not selected_suppliers:
                    st.error("Please select at least one supplier.")
                else:
                    try:
                        rfq_df.loc[rfq_df['rfq_id'] == selected_rfq, 'status'] = 'Sent'
                        org = st.session_state.user.get('organization', 'System')
                        rfq_df.to_csv(f"data/{org}/rfq.csv", index=False)
                        st.toast(f"✅ {selected_rfq} sent to {len(selected_suppliers)} suppliers.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating RFQ: {e}")
                
    with tab3:
        try:
            org = st.session_state.user.get('organization', 'System')
            df = pd.read_csv(f"data/{org}/rfq.csv")
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
        orders = fetch_data("api/orders")
        if orders:
            df = pd.DataFrame(orders)
            st.dataframe(df, use_container_width=True)
            render_export_buttons(df, "orders", "Order Monitoring")
        else:
            st.info("No data available.")
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
                                requests.put(f"{API_URL}/api/orders/{order.get('order_id')}/status", json={"status": "Approved"}, headers=get_auth_headers())
                                st.rerun()
                        with bcol2:
                            if st.button("Reject", key=f"rej_{order.get('order_id')}"):
                                requests.put(f"{API_URL}/api/orders/{order.get('order_id')}/status", json={"status": "Rejected"}, headers=get_auth_headers())
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
    
    st.subheader("My Profile")
    if st.session_state.user:
        with st.form("profile_form"):
            st.text_input("Role (Read-Only)", value=st.session_state.user.get('role', 'user'), disabled=True)
            st.text_input("Organization (Read-Only)", value=st.session_state.user.get('organization', 'System') or 'None', disabled=True)
            
            new_username = st.text_input("Username", value=st.session_state.user.get('username', ''))
            new_password = st.text_input("New Password (leave blank to keep current)", type="password")
            
            if st.form_submit_button("Update Profile"):
                payload = {}
                if new_username and new_username != st.session_state.user.get('username', ''):
                    payload["username"] = new_username
                if new_password:
                    payload["password"] = new_password
                    
                if payload:
                    try:
                        resp = requests.put(f"{API_URL}/api/users/me", json=payload, headers=get_auth_headers())
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.user = data["user"]
                            st.session_state.token = data["access_token"]
                            st.success("Profile updated securely! Your active session has been seamlessly refreshed.")
                        elif resp.status_code == 400 and "already taken" in resp.text:
                            st.error("That username is already taken by someone else.")
                        else:
                            st.error(f"Failed to update profile: {resp.text}")
                    except Exception as e:
                        st.error(f"Error connecting to server: {e}")
                else:
                    st.info("No changes were made.")
                    
    st.markdown("---")
    st.subheader("System Preferences")

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
