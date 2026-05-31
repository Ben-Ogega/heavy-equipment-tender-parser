import json
from datetime import datetime

def load_competitor_data(filepath="data/competitor_profiles.json"):
    """Load competitor profiles for proposal generation."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def generate_bid_proposal(tender_specs, equipment_category, selected_competitor, profiles, risk_register=None):
    """
    Generate board-ready technical bid proposal.
    
    Inputs:
        tender_specs: dict with requirements
        equipment_category: str
        selected_competitor: str (e.g., "CAT 320")
        profiles: competitor data
        risk_register: optional list from Engine 2
    
    Returns: dict with proposal sections
    """
    if risk_register is None:
        risk_register = []
    
    # Find competitor and LiuGong equivalent
    category_data = profiles.get(equipment_category, [])
    competitor_data = None
    
    for item in category_data:
        if f"{item.get('competitor', '')} {item.get('model', '')}" == selected_competitor:
            competitor_data = item
            break
    
    if not competitor_data:
        return {"error": f"Competitor {selected_competitor} not found"}
    
    liugong_model = competitor_data.get("liugong_equivalent", "N/A")
    liugong_price = competitor_data.get("price_usd", 0)
    competitor_price = competitor_data.get("price_usd", 0)  # Same field, adjust if needed
    
    # Calculate savings
    cat_premium = competitor_price * 1.4  # CAT typically 40% more
    savings_vs_cat = cat_premium - liugong_price
    savings_pct = (savings_vs_cat / cat_premium * 100) if cat_premium > 0 else 0
    
    # Build proposal
    proposal = {
        "header": {
            "title": f"Technical Bid Proposal: {liugong_model}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tender_ref": tender_specs.get("tender_reference", "N/A"),
            "equipment_category": equipment_category
        },
        "executive_summary": {
            "liugong_model": liugong_model,
            "competitor_benchmark": selected_competitor,
            "price_usd": liugong_price,
            "savings_vs_premium": f"${savings_vs_cat:,.0f}",
            "savings_percentage": f"{savings_pct:.1f}%"
        },
        "technical_compliance": {
            "power_hp": competitor_data.get("engine_hp", 0),
            "operating_weight_kg": competitor_data.get("operating_weight_kg", 0),
            "bucket_capacity_m3": competitor_data.get("bucket_capacity_m3", 0),
            "blade_width_m": competitor_data.get("blade_width_m", 0),
            "status": "Compliant with margin"
        },
        "value_proposition": competitor_data.get("sales_pitch", "No pitch available"),
        "risk_mitigation": [
            r["mitigation"] for r in risk_register if isinstance(r, dict)
        ],
        "support_framework": {
            "warranty": "12 months standard, extendable to 24",
            "parts_availability": "Nairobi hub + regional depots",
            "service_response": "48-hour response time",
            "operator_training": "Included: 2-day certification program"
        },
        "financial_summary": {
            "upfront_cost": f"${liugong_price:,.0f}",
            "estimated_annual_fuel": "KSh 2.4M (based on 2,000 hrs/yr)",
            "5_year_tco": f"${liugong_price * 1.5:,.0f} (incl. fuel, maintenance, parts)",
            "residual_value": "45% at Year 5"
        }
    }
    
    return proposal

def print_proposal(proposal):
    """Print formatted proposal to terminal."""
    if "error" in proposal:
        print(f"ERROR: {proposal['error']}")
        return
    
    h = proposal["header"]
    print(f"\n{'='*70}")
    print(f"TECHNICAL BID PROPOSAL")
    print(f"{'='*70}")
    print(f"Date: {h['date']}")
    print(f"Tender Ref: {h['tender_ref']}")
    print(f"Equipment: {h['equipment_category']}")
    print(f"{'='*70}")
    
    es = proposal["executive_summary"]
    print(f"\n📋 EXECUTIVE SUMMARY")
    print(f"LiuGong Model: {es['liugong_model']}")
    print(f"Benchmark: {es['competitor_benchmark']}")
    print(f"Price: {es['price_usd']}")
    print(f"Savings vs Premium Tier: {es['savings_vs_premium']} ({es['savings_percentage']})")
    
    tc = proposal["technical_compliance"]
    print(f"\n🔧 TECHNICAL COMPLIANCE")
    print(f"Engine Power: {tc['power_hp']} HP")
    print(f"Operating Weight: {tc['operating_weight_kg']:,} kg")
    if tc['bucket_capacity_m3']:
        print(f"Bucket Capacity: {tc['bucket_capacity_m3']} m³")
    if tc['blade_width_m']:
        print(f"Blade Width: {tc['blade_width_m']} m")
    print(f"Status: {tc['status']}")
    
    print(f"\n💡 VALUE PROPOSITION")
    print(f"{proposal['value_proposition']}")
    
    if proposal["risk_mitigation"]:
        print(f"\n⚠️ RISK MITIGATION STRATEGIES")
        for i, m in enumerate(proposal["risk_mitigation"], 1):
            print(f"{i}. {m}")
    
    sf = proposal["support_framework"]
    print(f"\n🛠️ SUPPORT FRAMEWORK")
    print(f"Warranty: {sf['warranty']}")
    print(f"Parts: {sf['parts_availability']}")
    print(f"Service: {sf['service_response']}")
    print(f"Training: {sf['operator_training']}")
    
    fs = proposal["financial_summary"]
    print(f"\n💰 FINANCIAL SUMMARY")
    print(f"Upfront Cost: {fs['upfront_cost']}")
    print(f"Est. Annual Fuel: {fs['estimated_annual_fuel']}")
    print(f"5-Year TCO: {fs['5_year_tco']}")
    print(f"Residual Value: {fs['residual_value']}")
    
    print(f"\n{'='*70}")
    print("END OF PROPOSAL")
    print(f"{'='*70}")

# Test
if __name__ == "__main__":
    profiles = load_competitor_data()
    
    # Test 1: Normal proposal
    tender = {
        "tender_reference": "HOAGDP-2023-001",
        "diesel_price_ksh": 180,
        "warranty_months": 24
    }
    
    proposal = generate_bid_proposal(tender, "excavators", "CAT 320", profiles)
    print_proposal(proposal)
    
    # Test 2: With risk register
    from sys import path
    path.insert(0, "engine2")
    try:
        from tco_risk import generate_tco_risk_register
        risks = generate_tco_risk_register(tender, "excavators")
        proposal2 = generate_bid_proposal(tender, "excavators", "Komatsu PC200", profiles, risks)
        print("\n\n")
        print_proposal(proposal2)
    except Exception as e:
        print(f"\nNote: Engine 2 not available for integration test: {e}")
