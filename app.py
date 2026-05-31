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

# Sidebar - Tender Specifications
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

# Sidebar - TCO Parameters
st.sidebar.markdown("---")
st.sidebar.subheader("TCO Parameters")

diesel_price = st.sidebar.number_input(
    "Diesel Price (KSh/L)",
    min_value=100,
    max_value=300,
    value=180
)

hours_per_day = st.sidebar.number_input(
    "Operating Hours/Day",
    min_value=1,
    max_value=24,
    value=8
)

days_per_year = st.sidebar.number_input(
    "Operating Days/Year",
    min_value=50,
    max_value=365,
    value=250
)

# TCO Calculation Function
def calculate_annual_fuel_cost(engine_hp, hours_per_day, days_per_year, diesel_price):
    """
    Rough estimate: 0.15 liters per HP per hour
    """
    liters_per_hour = engine_hp * 0.15
    total_liters = liters_per_hour * hours_per_day * days_per_year
    return int(total_liters * diesel_price)

# Run analysis
if st.sidebar.button("🔍 Analyze Tender", type="primary"):
    st.header("📊 Analysis Results")
    
    category_data = profiles.get(equipment_category, [])
    
    if not category_data:
        st.warning("No data available for this category")
    else:
        results = []
        for competitor in category_data:
            comp_hp = competitor.get("engine_hp", 0)
            score = 10 if comp_hp >= power_required else 0
            
            # Calculate TCO for this competitor
            annual_fuel = calculate_annual_fuel_cost(
                comp_hp, hours_per_day, days_per_year, diesel_price
            )
            
            results.append({
                "competitor": f"{competitor.get('competitor', 'Unknown')} {competitor.get('model', 'Unknown')}",
                "engine_hp": comp_hp,
                "liugong_equivalent": competitor.get("liugong_equivalent", "N/A"),
                "price_usd": competitor.get("price_usd", 0),
                "score": score,
                "annual_fuel_cost": annual_fuel,
                "sales_pitch": competitor.get("sales_pitch", "")
            })
        
        # Sort by score desc, then by annual fuel cost asc
        results.sort(key=lambda x: (-x["score"], x["annual_fuel_cost"]))
        
        # Display results
        for i, r in enumerate(results, 1):
            with st.container():
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    status = "✅ Compliant" if r["score"] > 0 else "❌ Below Spec"
                    st.write(f"**{i}. {r['competitor']}**")
                    st.write(f"Status: {status}")
                    st.write(f"Power: {r['engine_hp']} HP")
                    st.write(f"Price: ${r['price_usd']:,}")
                
                with col2:
                    st.info(f"**LiuGong Alternative: {r['liugong_equivalent']}**")
                    st.write(f"🎯 {r['sales_pitch']}")
                    st.write(f"💰 Est. Annual Fuel: KSh {r['annual_fuel_cost']:,}")
                
                st.divider()
        
        # Best recommendation
        if results:
            best = results[0]
            st.success(f"""
            **🏆 RECOMMENDED: {best['liugong_equivalent']}**
            
            - Compliance Score: {best['score']}/10
            - Est. Annual Fuel Cost: KSh {best['annual_fuel_cost']:,}
            - Upfront Price: ${best['price_usd']:,}
            
            Use this in your tender response.
            """)

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Built by Ben Ogega | LiuGong East Africa")
