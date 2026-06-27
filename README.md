# Decentralized Multi-Agent Supply Chain Optimizer (Enterprise Edition)

🚀 **Live Application:** [https://supply-chain-optimaizer-sm.streamlit.app/](https://supply-chain-optimaizer-sm.streamlit.app/)

![Dashboard](docs/dashboard.png)

## 🏢 Project Overview
The **Decentralized Multi-Agent Supply Chain Optimizer** is a state-of-the-art, AI-powered procurement and logistics intelligence platform. Designed as a modern enterprise SaaS application, it leverages intelligent, autonomous AI agents to fundamentally transform traditional supply chain management. 

By coordinating demand forecasting, inventory analysis, supplier selection, contract negotiation, and route optimization autonomously, this platform reduces procurement costs, prevents stockouts, and mitigates global supply chain risks in real-time.

---

## ✨ Advanced Enterprise Features

- **Multi-Agent Orchestration**: Utilizes CrewAI and LangGraph to coordinate a swarm of specialized AI agents working in tandem.
- **🤝 AI Contract Negotiator**: An advanced CrewAI agent that autonomously drafts negotiation strategies, bulk discount proposals, and counter-offers based on live supplier data.
- **Cloud-Native Architecture**: Deployed with a separated frontend (Streamlit Community Cloud) and backend (FastAPI on Render), powered by a highly scalable Supabase PostgreSQL database.
- **Enterprise UI/UX**: Built with a stunning Glassmorphism design system supporting native Light/Dark modes, intelligent data caching, dynamic routing, toast notifications, and interactive data tables with vibrant gradient buttons.
- **Role-Based Access Control (RBAC)**: Fully integrated JWT authentication with distinct User and Admin access levels.
- **Dynamic Command Center**: A sleek, reactive dashboard featuring live KPIs and interactive Plotly visualizations (Spend Analysis, Status Distribution, Inventory Health, Supplier Ratings).
- **Automated RFQ & Procurement**: Seamlessly create, send, and track Procurement Requests and RFQs with automated AI-driven supplier quotation comparisons.
- **One-Click Exporting**: Instantly export complex data grids to CSV, Excel, and PDF formats for executive reporting.

---

## 🤖 AI Agents Architecture

The core of the platform is powered by a decentralized network of specialized AI agents powered by NVIDIA Llama 3.1 70B:

1. **🤝 Negotiator Agent (NEW)**: Prepares sophisticated bulk-discount negotiation emails and pricing strategies.
2. **📈 Forecast Agent**: Analyzes historical data and market signals to predict demand trends, ensuring optimal stock levels.
3. **📦 Inventory Agent**: Continuously monitors warehouse stock levels against thresholds to automatically flag replenishment needs.
4. **🛒 Procurement Agent**: Synthesizes data from the entire network to generate cost-effective purchase recommendations.
5. **🏭 Supplier Agent**: Evaluates and selects the optimal supplier based on real-time pricing, delivery schedules, and historical reliability.
6. **⚠️ Risk Agent**: Scans geopolitical, environmental, and logistical data to evaluate and mitigate supply chain disruptions proactively.
7. **🚚 Route Agent**: Calculates the most efficient logistics and delivery routes to minimize transit times and reduce freight costs.

---

## 📁 Folder Structure

```text
supply-chain-optimizer/
├── backend/
│   ├── agents/          # CrewAI agents (Negotiator, Supplier, etc.)
│   ├── database/        # SQLAlchemy ORM models (Supabase connection)
│   ├── models/          # Pydantic schemas for API validation
│   ├── services/        # Business logic and Orchestration
│   ├── workflow/        # LangGraph coordination workflow
│   ├── main.py          # FastAPI application entry point
│   ├── auth.py          # JWT Authentication logic
├── data/                # Local data storage and CSV datasets
├── docs/                # Project screenshots and documentation assets
├── frontend/
│   ├── app.py           # Streamlit enterprise application
│   ├── requirements.txt # Frontend-specific dependencies (for Streamlit Cloud)
├── requirements.txt     # Global dependencies (for Render Backend)
└── README.md
```

---

## 🚀 Installation & Execution

### Local Setup (FastAPI + Streamlit)

1. **Clone the repository and create a virtual environment:**
```bash
git clone https://github.com/your-username/supply-chain-optimizer.git
cd supply-chain-optimizer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set Environment Variables:**
Create a `.env` file in the root directory:
```env
NVIDIA_API_KEY="your-nvidia-key"
SECRET_KEY="your-jwt-secret-key"
DATABASE_URL="postgresql://postgres:[password]@aws-0-pooler.supabase.com:6543/postgres"
API_URL="http://localhost:8000"
```

4. **Launch the Backend API:**
```bash
python -m uvicorn backend.main:app --reload
```

5. **Launch the Enterprise Dashboard (New Terminal):**
```bash
python -m streamlit run frontend/app.py
```

---

## 🔌 API Documentation

Once the backend is running, you can access the interactive Swagger UI at: `http://127.0.0.1:8000/docs` (or your live Render URL `/docs`).

**Core Endpoints:**
- `POST /api/auth/login` - Authenticate and receive JWT token
- `POST /api/negotiate` - Trigger the AI Contract Negotiator Agent
- `GET /api/orders` - Retrieve live order tracking
- `GET /suppliers` - Fetch active supplier network
- `POST /optimize` - Run the full end-to-end multi-agent workflow

---
*Developed as a demonstration of advanced Multi-Agent Systems (MAS) applied to modern Enterprise Resource Planning (ERP).*
