import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Pokemon Test App", layout="wide")
st.title("Pokémon API Connectivity Test")

API_URL = "https://api.pokemontcg.io/v2/cards"

@st.cache_data(ttl=3600)
def load_cards():
    headers = {
        "User-Agent": "streamlit-test/1.0",
        "X-Api-Key": st.secrets["POKEMON_TCG_API_KEY"],
    }

    params = {
        "pageSize": 50,
        "select": "id,name,set.name,tcgplayer.prices"
    }

    r = requests.get(API_URL, headers=headers, params=params, timeout=15)
    r.raise_for_status()

    rows = []
    for c in r.json()["data"]:
        prices = c.get("tcgplayer", {}).get("prices", {})
        price = (
            prices.get("holofoil", {}) or
            prices.get("normal", {})
        ).get("market")

        if price:
            rows.append({
                "Card": c["name"],
                "Set": c["set"]["name"],
                "Raw Price": round(price, 2)
            })

    return pd.DataFrame(rows)

try:
    df = load_cards()
    st.success(f"Loaded {len(df)} cards")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error("API call failed")
    st.code(str(e))
