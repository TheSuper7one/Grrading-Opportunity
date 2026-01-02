import streamlit as st
import requests
import pandas as pd

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(
    page_title="Pokémon Grading Opportunity Finder",
    layout="wide"
)

st.title("🃏 Pokémon Grading Opportunity Dashboard")
st.caption("Live raw pricing data • Graded pricing coming next")

# -----------------------------
# Data Fetching
# -----------------------------
API_URL = "https://api.pokemontcg.io/v2/cards"

@st.cache_data(ttl=3600)
def fetch_cards(page_size=100):
    params = {
        "pageSize": page_size,
        "select": "id,name,set,tcgplayer"
    }

    response = requests.get(API_URL, params=params)
    response.raise_for_status()

    cards = response.json()["data"]
    rows = []

    for card in cards:
        prices = card.get("tcgplayer", {}).get("prices", {})

        # Prefer holofoil, then normal
        price_data = prices.get("holofoil") or prices.get("normal")

        if not price_data:
            continue

        raw_price = price_data.get("market")

        if raw_price is None:
            continue

        rows.append({
            "card_id": card["id"],
            "card_name": card["name"],
            "set": card["set"]["name"],
            "raw_price": round(raw_price, 2),
            "psa9_price": None,
            "psa10_price": None
        })

    return pd.DataFrame(rows)

# -----------------------------
# Load Data
# -----------------------------
with st.spinner("Fetching Pokémon card prices..."):
    df = fetch_cards()

if df.empty:
    st.warning("No pricing data returned.")
    st.stop()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

sets = sorted(df["set"].unique())

selected_sets = st.sidebar.multiselect(
    "Pokémon Set",
    options=sets,
    default=[]
)

max_raw_price = st.sidebar.slider(
    "Maximum Raw Price ($)",
    min_value=0,
    max_value=int(df["raw_price"].max()),
    value=100
)

grading_cost = st.sidebar.number_input(
    "Estimated Grading Cost ($)",
    value=25,
    step=5
)

# -----------------------------
# Apply Filters
# -----------------------------
filtered = df.copy()

if selected_sets:
    filtered = filtered[filtered["set"].isin(selected_sets)]

filtered = filtered[filtered["raw_price"] <= max_raw_price]

# -----------------------------
# Placeholder Grading Logic
# -----------------------------
filtered["psa10_profit"] = None
filtered["roi_percent"] = None

# -----------------------------
# Metrics
# -----------------------------
st.subheader("📊 Results Overview")

col1, col2 = st.columns(2)

col1.metric("Cards Found", len(filtered))
col2.metric("Avg Raw Price", f"${filtered['raw_price'].mean():.2f}")

# -----------------------------
# Results Table
# -----------------------------
st.subheader("🧾 Card Results")

st.write(filtered.head())
st.dataframe(
    filtered.sort_values("raw_price", ascending=False),
    use_container_width=True
)

