import streamlit as st
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Heavy Equipment Tender Parser",
    page_icon="🏗️",
    layout="wide"
)

# Title
st.title("🏗️ Heavy Equipment Tender Parser")
st.subheader("Automated compliance analysis for East African tenders")

# Load data
@st.cache_data
def load_profiles():
    try:
        with open("data/competitor_profiles.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

profiles = load_profiles()

# Sidebar
st.sidebar.header("Tender Specifications")

equipment_category = st.sidebar.selectbox(
    "Equipment Category",
    list(profiles.keys()) if profiles else ["excavators", "wheel_loaders", "motor_graders"]
)

power_required = st.sidebar.number_input(
    "Required Engine Power (HP)",
    min_value=50,
    max_value=500,
    value=180
)

# Tender specs dict
tender_specs = {"engine_hp": power_required}

# Run analysis button
if st.sidebar.button("🔍 Analyze Tender", type="primary"):
    st.header("📊 Analysis Results")
    
    category_data = profiles.get(equipment_category, [])
    
    if not category_data:
        st.warning("No competitor data available for this category")
    else:
        # Simple scoring (reusing logic from tender_analyzer)
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
        
        # Sort by score desc, price asc
        results.sort(key=lambda x: (-x["score"], x["price_usd"]))
        
        # Display results
        for i, r in enumerate(results, 1):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 3])
                
                with col1:
                    st.write(f"**{i}. {r['competitor']}**")
                    st.write(f"Power: {r['engine_hp']} HP")
                
                with col2:
                    status = "✅ Compliant" if r["score"] > 0 else "❌ Below Spec"
                    st.write(f"**{status}**")
                    st.write(f"${r['price_usd']:,}")
                
                with col3:
                    st.info(f"LiuGong Alternative: **{r['liugong_equivalent']}**")
                    st.write(f"🎯 {r['sales_pitch']}")
                
                st.divider()
        
        # Best recommendation
        best = results[0] if results else None
        if best:
            st.success(f"""
            **RECOMMENDED: {best['liugong_equivalent']}**
            
            Highest compliance score with competitive pricing.
            Use this in your tender response.
            """)
