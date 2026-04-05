from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

# ---------------------------
# Load Data
# ---------------------------
with open("q-fastapi-llm-query.json") as f:
    data = json.load(f)

app = FastAPI()

# ---------------------------
# Enable CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Normalize helper
# ---------------------------
def normalize(text):
    return text.lower().strip()

# ---------------------------
# Extractors
# ---------------------------
def find_product(q):
    products = ["chicken", "bacon", "sausages", "keyboard", "computer", "soap", "cheese", "pants", "shoes"]
    for p in products:
        if p in q:
            return p.capitalize()
    return None

def find_city(q):
    for d in data:
        city = d["city"]
        if normalize(city) in q:
            return city
    return None

def find_region(q):
    for d in data:
        region = d["region"]
        if normalize(region) in q:
            return region
    return None

def find_rep(q):
    for d in data:
        name = d["rep"]
        parts = normalize(name).split()
        if all(part in q for part in parts):
            return name
    return None

# ---------------------------
# Core Logic
# ---------------------------
def answer_question(q: str):
    q = normalize(q)

    product = find_product(q)
    city = find_city(q)
    region = find_region(q)
    rep = find_rep(q)

    # Flexible matching
    def match(d):
        if product and normalize(product) not in normalize(d["product"]):
            return False
        if city and normalize(city) not in normalize(d["city"]):
            return False
        if region and normalize(region) not in normalize(d["region"]):
            return False
        if rep and normalize(rep) not in normalize(d["rep"]):
            return False
        return True

    filtered = [d for d in data if match(d)]

    # ---------------------------
    # Question Types
    # ---------------------------

    # TOTAL
    if "total sales" in q:
        return sum(d["sales"] for d in filtered)

    # AVERAGE
    if "average" in q:
        values = [d["sales"] for d in filtered]
        return round(sum(values) / len(values), 2) if values else 0

    # COUNT REPS
    if "how many sales reps" in q:
        reps = set(d["rep"] for d in filtered)
        return len(reps)

    # HIGHEST SALE DATE
    if "highest sale" in q:
        if not filtered:
            return None
        max_item = max(filtered, key=lambda x: x["sales"])
        return max_item["date"]

    return "Question not understood"

# ---------------------------
# API Endpoint
# ---------------------------
@app.get("/query")
def query(q: str):
    result = answer_question(q)

    response = JSONResponse(content={"answer": result})
    response.headers["X-Email"] = "23f1002787@ds.study.iitm.ac.in"

    return response