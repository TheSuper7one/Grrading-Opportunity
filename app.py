import streamlit as st
import requests
import pandas as pd
from requests.exceptions import Timeout, RequestException

st.set_page_config(page_title="Pokemon Price Test", layout="wide")
st.title("🧪 Pokémon API Connectivity Test (Free Tier Safe)")

API_URL = "https://api.pokemontcg.io/v2/cards"

def fetch_cards(page=1, page_size=25):
    headers = {
        "User-Agent": "streamlit-free-tier/1.0",
        "X-Api-Key": st.secrets["POKEMON_TCG_API_KEY"]
    }

    params = {
        "page": page,
        "pageSize": page_size,
        "select": "id,name,set.name,tcgplayer.prices"
    }

    response = requests.get(
        API_URL,
        headers=headers,
        params=params,
        timeout=8  # LOWER timeout = faster failure
    )

    response.raise_for_status()
    return response.json()["data"]

st.info(
    "This app is optimized for Streamlit Cloud Free Tier.\n"
    "Click the button to load a small page of cards."
)

if st.button("Load Pokémon Cards"):
    with st.spinner("Fetching cards..."):
        try:
            cards = fetch_cards()

            rows = []
            for c in cards:
                prices = c.get("tcgplayer", {}).get("prices", {})
                price = (
                    prices.get("holofoil", {}) or
                    prices.get("normal", {})
                ).get("market")

                if price:
                    rows.append({
                        "Card": c["name"],
                        "Set": c["set"]["name"],
                        "Raw Price ($)": round(price, 2)
                    })

            df = pd.DataFrame(rows)

            if df.empty:
                st.warning("No priced cards returned.")
            else:
                st.success(f"Loaded {len(df)} cards")
                st.dataframe(df, use_container_width=True)

        except Timeout:
            st.error(
                "Request timed out.\n\n"
                "This is common on Streamlit Cloud free tier.\n"
                "Click the button again."
            )

        except RequestException as e:
            st.error("API request failed")
            st.code(str(e))
