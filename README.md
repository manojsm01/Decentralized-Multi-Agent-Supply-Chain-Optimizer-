# Decentralized Multi-Agent Supply Chain Optimizer (Enterprise Edition)

![Dashboard](docs/dashboard.png)

## 🏢 Project Overview
The **Decentralized Multi-Agent Supply Chain Optimizer** is a state-of-the-art, AI-powered procurement and logistics intelligence platform. Designed as a modern enterprise SaaS application, it leverages intelligent, autonomous AI agents to fundamentally transform traditional supply chain management. 

By coordinating demand forecasting, inventory analysis, supplier selection, risk assessment, and route optimization autonomously, this platform reduces procurement costs, prevents stockouts, and mitigates global supply chain risks in real-time.

---

## ✨ Key Enterprise Features

- **Multi-Agent Orchestration**: Utilizes CrewAI and LangGraph to coordinate a swarm of specialized AI agents working in tandem.
- **Dynamic Command Center**: A sleek, reactive dashboard featuring 8 live KPIs and 4 interactive Plotly visualizations (Spend Analysis, Status Distribution, Inventory Health, Supplier Ratings).
- **Automated RFQ & Procurement**: Seamlessly create, send, and track Procurement Requests and RFQs with automated AI-driven supplier quotation comparisons.
- **Enterprise UI/UX**: Built with a premium, responsive design system supporting native Light/Dark modes, intelligent data caching, toast notifications, and interactive data tables.
- **Comprehensive Data Management**: Built-in CSV ingestion and synchronization for Suppliers, Inventory, Orders, Routes, RFQs, and Procurement Requests.
- **One-Click Exporting**: Instantly export complex data grids to CSV, Excel, and PDF formats for executive reporting.

---

## 🤖 AI Agents Architecture

The core of the platform is powered by a decentralized network of specialized AI agents:

1. **📈 Forecast Agent**: Analyzes historical data and market signals to predict demand trends, ensuring optimal stock levels.
2. **📦 Inventory Agent**: Continuously monitors warehouse stock levels against thresholds to automatically flag replenishment needs.
3. **🛒 Procurement Agent**: Synthesizes data from the entire network to generate cost-effective purchase recommendations.
4. **🏭 Supplier Agent**: Evaluates and selects the optimal supplier based on real-time pricing, delivery schedules, and historical reliability.
5. **⚠️ Risk Agent**: Scans geopolitical, environmental, and logistical data to evaluate and mitigate supply chain disruptions proactively.
6. **🚚 Route Agent**: Calculates the most efficient logistics and delivery routes to minimize transit times and reduce freight costs.

---

## 📁 Folder Structure

```text
supply-chain-optimizer/
├── backend/
│   ├── agents/          # Individual CrewAI agent logic
│   ├── database/        # SQLAlchemy ORM models and CRUD operations
│   ├── models/          # Pydantic schemas for API validation
│   ├── services/        # Business logic and Orchestration
│   ├── workflow/        # LangGraph coordination workflow
│   ├── main.py          # FastAPI application entry point
├── data/                # Local data storage and CSV datasets
├── docs/                # Project screenshots and documentation assets
├── frontend/
│   ├── app.py           # Streamlit enterprise application
│   ├── requirements.txt # Frontend-specific dependencies
├── docker-compose.yml   # Docker deployment configuration
├── requirements.txt     # Global dependencies
└── README.md
```

---

## 🚀 Installation & Execution

### Local Setup (SQLite + FastAPI + Streamlit)

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
Create a `.env` file in the root directory and add your AI provider API keys:
```env
GOOGLE_API_KEY=your_api_key_here
# OPENAI_API_KEY=optional_alternative
```

4. **Launch the Backend API:**
```bash
python -m uvicorn backend.main:app --reload
```

5. **Launch the Enterprise Dashboard (New Terminal):**
```bash
python -m streamlit run frontend/app.py
```

### Docker Deployment

To run the entire stack (including PostgreSQL) via Docker Compose:
```bash
docker-compose up --build
```

---

## 🔌 API Documentation

Once the backend is running, you can access the interactive Swagger UI at: `http://127.0.0.1:8000/docs`

**Core Endpoints:**
- `GET /api/orders` - Retrieve live order tracking
- `GET /suppliers` - Fetch active supplier network
- `POST /api/forecast` - Trigger the Forecast Agent
- `POST /api/suppliers/recommend` - Trigger the Supplier Agent
- `POST /api/inventory/analyze` - Trigger the Inventory Agent
- `POST /optimize` - Run the full end-to-end multi-agent workflow

---
*Developed as a demonstration of advanced Multi-Agent Systems (MAS) applied to modern Enterprise Resource Planning (ERP).*
