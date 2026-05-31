import streamlit as st
import json

st.set_page_config(page_title="Heavy Equipment Tender Parser", page_icon="🏗️")

st.title("🏗️ Heavy Equipment Tender Parser")
st.subheader("Automated compliance analysis for East African tenders")

# Load data
def load_profiles():
    try:
        with open("data/competitor_profiles.json", "r") as f:
            return json.load(f)
    except:
        return {}

profiles = load_profiles()

# Sidebar
st.sidebar.header("Tender Specifications")

equipment_category = st.sidebar.selectbox(
    "Equipment Category",
    list(profiles.keys()) if profiles else ["excavators"]
)

power_required = st.sidebar.number_input(
    "Required Engine Power (HP)",
    min_value=50,
    max_value=500,
    value=180
)

# Run analysis
if st.sidebar.button("Analyze Tender"):
    st.header("Analysis Results")
    
    category_data = profiles.get(equipment_category, [])
    
    if not category_data:
        st.warning("No data available")
    else:
        results = []
        for competitor in category_data:
            comp_hp = competitor.get("engine_hp", 0)
            score = 10 if comp_hp >= power_required else 0
            
            results.append({
                "competitor": f"{competitor.get('competitor', 'Unknown')} {competitor.get('model', 'Unknown')}",
                "engine_hp": comp_hp,
                "liugong_equivalent": competitor.get("liugong_equivalent", "N/A"),
                "price_usd": competitor.get("price_usd", 0),
                "score": score,
                "sales_pitch": competitor.get("sales_pitch", "")
            })
        
        results.sort(key=lambda x: (-x["score"], x["price_usd"]))
        
        for i, r in enumerate(results, 1):
            status = "Compliant" if r["score"] > 0 else "Below Spec"
            st.write(f"**{i}. {r['competitor']}** — {status}")
            st.write(f"Power: {r['engine_hp']} HP | Price: ${r['price_usd']:,}")
            st.write(f"LiuGong Alternative: **{r['liugong_equivalent']}**")
            st.write(f"Pitch: {r['sales_pitch']}")
            st.write("---")
        
        if results:
            best = results[0]
            st.success(f"RECOMMENDED: {best['liugong_equivalent']}")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Built by Ben Ogega | LiuGong East Africa")
