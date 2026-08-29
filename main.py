import sqlite3
import re
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="M&P Studio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"
DB_PATH = "mp_studio.db"


class ChatRequest(BaseModel):
    message: str


KNOWLEDGE_BASE = [
    {
        "topic": "warranty",
        "keywords": ["warranty", "repair", "samsung", "device"],
        "content": "M&P handles Samsung device warranty fulfillment. Devices sent for repair are logged, tracked through the courier network, and returned to the customer within 7-10 business days."
    },
    {
        "topic": "dcrs",
        "keywords": ["dcrs", "field visit", "check-in", "location verification"],
        "content": "DCRS is used by pharma field representatives to log pharmacy and doctor visits, verifying attendance via location-based check-in."
    },
    {
        "topic": "returns",
        "keywords": ["return", "refund", "exchange"],
        "content": "Products ordered through AppTak cannot be returned or exchanged once the order is confirmed, in line with standard pharmaceutical distribution practice."
    },
]


def search_knowledge_base(query):
    query_lower = query.lower()
    best_match = None
    best_score = 0
    for doc in KNOWLEDGE_BASE:
        score = sum(1 for kw in doc["keywords"] if kw in query_lower)
        if score > best_score:
            best_score = score
            best_match = doc
    return best_match


def classify_intent(message):
    msg = message.lower()

    if re.search(r"sup-\d+", msg) or "ticket" in msg or ("repair" in msg and "samsung" in msg):
        return "support_lookup"
    if "stock" in msg or "inventory" in msg or "warehouse" in msg:
        return "warehouse_lookup"
    if re.search(r"apt-\d+", msg) or "order" in msg:
        return "order_lookup"
    if re.search(r"trk-\d+", msg) or "shipment" in msg or "tracking" in msg or "delivery" in msg:
        return "shipment_lookup"
    if "telecom" in msg and ("sales" in msg or "revenue" in msg):
        return "telecom_sales_lookup"
    if "sales" in msg or "revenue" in msg or "units sold" in msg:
        return "sales_lookup"
    if "visit" in msg or "field rep" in msg or ("pharmacy" in msg and "warranty" not in msg):
        return "visit_lookup"

    return "knowledge_base"


def run_query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def query_order(message):
    match = re.search(r"apt-\d+", message.lower())
    if match:
        return run_query("SELECT * FROM orders WHERE order_number = ?", (match.group(0).upper(),))
    return run_query("SELECT * FROM orders ORDER BY created_at DESC LIMIT 5")


def query_shipment(message):
    match = re.search(r"trk-\d+", message.lower())
    if match:
        return run_query("SELECT * FROM shipments WHERE tracking_id = ?", (match.group(0).upper(),))
    return run_query("SELECT * FROM shipments ORDER BY last_updated DESC LIMIT 5")


def query_sales(message):
    return run_query(
        "SELECT rep_name, department, SUM(units_sold) as total_units, SUM(revenue) as total_revenue "
        "FROM sales_activity WHERE department = 'pharma_sales' GROUP BY rep_name ORDER BY total_revenue DESC"
    )


def query_telecom_sales(message):
    return run_query(
        "SELECT rep_name, department, SUM(units_sold) as total_units, SUM(revenue) as total_revenue "
        "FROM sales_activity WHERE department = 'telecom_sales' GROUP BY rep_name ORDER BY total_revenue DESC"
    )


def query_visits(message):
    return run_query("SELECT * FROM field_visits ORDER BY visit_date DESC LIMIT 5")


def query_support(message):
    match = re.search(r"sup-\d+", message.lower())
    if match:
        return run_query("SELECT * FROM support_tickets WHERE ticket_number = ?", (match.group(0).upper(),))
    return run_query("SELECT * FROM support_tickets ORDER BY created_at DESC LIMIT 5")


def query_warehouse(message):
    return run_query(
        "SELECT product_name, warehouse_location, quantity_available FROM warehouse_stock "
        "ORDER BY quantity_available ASC LIMIT 8"
    )


def ask_ollama(prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"]


ROUTES = {
    "order_lookup": (query_order, "structured_query (orders)"),
    "shipment_lookup": (query_shipment, "structured_query (shipments)"),
    "sales_lookup": (query_sales, "structured_query (pharma sales)"),
    "telecom_sales_lookup": (query_telecom_sales, "structured_query (telecom sales)"),
    "visit_lookup": (query_visits, "structured_query (field visits)"),
    "support_lookup": (query_support, "structured_query (support tickets)"),
    "warehouse_lookup": (query_warehouse, "structured_query (warehouse stock)"),
}


@app.post("/chat")
def chat(req: ChatRequest):
    intent = classify_intent(req.message)

    if intent in ROUTES:
        query_fn, source = ROUTES[intent]
        data = query_fn(req.message)
        prompt = (
            f"You are M&P Studio AI, an internal assistant for Muller & Phipps covering pharma, "
            f"telecom, logistics and customer support. A user asked: \"{req.message}\"\n\n"
            f"Here is the exact data from the relevant department database:\n{data}\n\n"
            f"Answer the user's question clearly and concisely using ONLY this data. "
            f"If nothing matches, say so directly."
        )
    else:
        doc = search_knowledge_base(req.message)
        if doc:
            prompt = (
                f"You are M&P Studio AI. A user asked: \"{req.message}\"\n\n"
                f"Here is relevant internal documentation:\n{doc['content']}\n\n"
                f"Answer using this information."
            )
            source = f"knowledge_base ({doc['topic']})"
        else:
            prompt = (
                f"You are M&P Studio AI. A user asked: \"{req.message}\"\n\n"
                f"No matching internal data was found. Politely say you don't have information "
                f"on this yet, without making anything up."
            )
            source = "no_match"

    answer = ask_ollama(prompt)

    return {"answer": answer, "routing": intent, "source": source}


@app.get("/dashboard")
def dashboard():
    order_status = run_query("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
    orders_by_type = run_query("SELECT order_type, COUNT(*) as count FROM orders GROUP BY order_type")
    pharma_sales = run_query(
        "SELECT rep_name, SUM(revenue) as revenue FROM sales_activity WHERE department = 'pharma_sales' GROUP BY rep_name"
    )
    telecom_sales = run_query(
        "SELECT rep_name, SUM(revenue) as revenue FROM sales_activity WHERE department = 'telecom_sales' GROUP BY rep_name"
    )
    support_status = run_query("SELECT status, COUNT(*) as count FROM support_tickets GROUP BY status")
    shipment_status = run_query("SELECT status, COUNT(*) as count FROM shipments GROUP BY status")
    low_stock = run_query(
        "SELECT product_name, warehouse_location, quantity_available FROM warehouse_stock "
        "ORDER BY quantity_available ASC LIMIT 5"
    )
    totals = run_query(
        "SELECT (SELECT COUNT(*) FROM orders) as total_orders, "
        "(SELECT COUNT(*) FROM support_tickets) as total_tickets, "
        "(SELECT COUNT(*) FROM field_visits) as total_visits, "
        "(SELECT ROUND(SUM(revenue)) FROM sales_activity) as total_revenue"
    )[0]

    return {
        "order_status": order_status,
        "orders_by_type": orders_by_type,
        "pharma_sales": pharma_sales,
        "telecom_sales": telecom_sales,
        "support_status": support_status,
        "shipment_status": shipment_status,
        "low_stock": low_stock,
        "totals": totals,
    }


@app.get("/")
def health():
    return {"status": "M&P Studio AI backend running"}