import json
import sys
from datetime import datetime
from pathlib import Path

def load_diesel_data(filepath="data/kenya_diesel_prices.json"):
    """
    Load historical diesel price data.
    Returns list or empty list on any error.
    """
    try:
        # Try multiple path resolutions
        paths_to_try = [
            Path(filepath),
            Path(__file__).parent.parent / filepath,
            Path.cwd() / filepath
        ]
        
        file_path = None
        for p in paths_to_try:
            if p.exists():
                file_path = p
                break
        
        if file_path is None:
            print(f"WARNING: Diesel data file not found at {filepath}")
            return []
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Validate structure
        if not isinstance(data, list):
            print(f"WARNING: Diesel data should be list, got {type(data).__name__}")
            return []
        
        # Validate each entry has required fields
        valid_entries = []
        for i, entry in enumerate(data):
            if isinstance(entry, dict) and "price" in entry:
                try:
                    float(entry["price"])  # Validate numeric
                    valid_entries.append(entry)
                except (ValueError, TypeError):
                    print(f"WARNING: Invalid price at index {i}: {entry.get('price')}")
            else:
                print(f"WARNING: Skipping invalid entry at index {i}")
        
        return valid_entries
        
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}")
        return []
    except PermissionError:
        print(f"ERROR: Permission denied reading {filepath}")
        return []
    except Exception as e:
        print(f"ERROR: Unexpected error loading diesel data: {e}")
        return []

def calculate_volatility_risk(current_price, historical_prices):
    """
    Calculate price volatility risk based on historical data.
    Returns: (risk_level, projected_low, projected_high)
    """
    # Validate inputs
    if not isinstance(current_price, (int, float)):
        try:
            current_price = float(current_price)
        except (ValueError, TypeError):
            print(f"WARNING: Invalid current_price: {current_price}")
            return "UNKNOWN", 0, 0
    
    if current_price <= 0:
        print(f"WARNING: current_price must be positive, got {current_price}")
        return "UNKNOWN", 0, 0
    
    # Handle empty historical data
    if not historical_prices:
        print("INFO: No historical data, using default 10% volatility")
        return "LOW", current_price * 0.9, current_price * 1.1
    
    # Extract and validate prices
    prices = []
    for i, entry in enumerate(historical_prices):
        try:
            price = float(entry.get("price", 0))
            if price > 0:
                prices.append(price)
            else:
                print(f"WARNING: Non-positive price at index {i}: {price}")
        except (ValueError, TypeError, AttributeError) as e:
            print(f"WARNING: Invalid price at index {i}: {e}")
    
    if len(prices) < 2:
        print(f"INFO: Only {len(prices)} valid price points, using default")
        return "LOW", current_price * 0.9, current_price * 1.1
    
    # Calculate statistics
    try:
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
        
        if avg_price <= 0:
            return "UNKNOWN", current_price * 0.9, current_price * 1.1
        
        volatility = (max_price - min_price) / avg_price
        
        # Clamp volatility to reasonable range
        volatility = max(0.0, min(volatility, 1.0))
        
        # Determine risk level
        if volatility > 0.30:
            risk = "CRITICAL"
        elif volatility > 0.20:
            risk = "HIGH"
        elif volatility > 0.10:
            risk = "MEDIUM"
        else:
            risk = "LOW"
        
        # Calculate projections with bounds
        projected_low = current_price * (1 - volatility * 0.5)
        projected_high = current_price * (1 + volatility * 0.5)
        
        # Ensure low doesn't go below zero
        projected_low = max(0, projected_low)
        
        return risk, projected_low, projected_high
        
    except Exception as e:
        print(f"ERROR: Calculation failed: {e}")
        return "UNKNOWN", current_price * 0.9, current_price * 1.1

def calculate_warranty_risk(warranty_months, equipment_category):
    """
    Assess warranty risk based on standard vs. tender requirements.
    Returns: (risk_level, description)
    """
    # Validate warranty_months
    try:
        warranty_months = int(warranty_months)
    except (ValueError, TypeError):
        return "UNKNOWN", f"Invalid warranty period: {warranty_months}"
    
    if warranty_months < 0:
        return "UNKNOWN", f"Negative warranty period: {warranty_months}"
    
    # Standard warranties by category
    standard_warranty = {
        "excavators": 12,
        "wheel_loaders": 12,
        "motor_graders": 12,
        "bulldozers": 12,
        "rollers": 12,
        "forklifts": 12
    }
    
    # Handle unknown category
    standard = standard_warranty.get(equipment_category, 12)
    
    # Calculate risk
    if warranty_months == 0:
        return "LOW", "No warranty required"
    
    ratio = warranty_months / standard if standard > 0 else 0
    
    if ratio > 3.0:
        return "CRITICAL", f"Warranty {warranty_months}mo exceeds standard {standard}mo by 200%+"
    elif ratio > 2.0:
        return "HIGH", f"Extended warranty {warranty_months}mo is 100%+ above standard {standard}mo"
    elif ratio > 1.5:
        return "MEDIUM", f"Extended warranty {warranty_months}mo 50% above standard {standard}mo"
    elif ratio > 1.0:
        return "LOW", f"Extended warranty {warranty_months}mo moderately above standard {standard}mo"
    else:
        return "LOW", f"Standard warranty {warranty_months}mo within normal range"

def generate_tco_risk_register(tender_specs, equipment_category, profiles=None):
    """
    Generate comprehensive TCO risk register for tender.
    Returns list of risk dicts.
    """
    # Validate inputs
    if not isinstance(tender_specs, dict):
        print(f"ERROR: tender_specs must be dict, got {type(tender_specs).__name__}")
        return []
    
    if not isinstance(equipment_category, str):
        print(f"WARNING: equipment_category should be string, got {type(equipment_category).__name__}")
        equipment_category = str(equipment_category).lower().replace(" ", "_")
    
    risks = []
    
    # Price volatility risk
    try:
        current_diesel = tender_specs.get("diesel_price_ksh", 180)
        if current_diesel is None:
            current_diesel = 180
        current_diesel = float(current_diesel)
        
        diesel_data = load_diesel_data()
        vol_risk, low, high = calculate_volatility_risk(current_diesel, diesel_data)
        
        risks.append({
            "risk_id": "FUEL-001",
            "category": "Fuel Price Volatility",
            "severity": vol_risk,
            "current_value": f"KSh {current_diesel:.2f}/L",
            "projected_range": f"KSh {low:.2f} - KSh {high:.2f}",
            "mitigation": "Fix fuel price for first 12 months via supplier contract or hedge via forward purchase"
        })
    except Exception as e:
        print(f"WARNING: Fuel risk calculation failed: {e}")
        risks.append({
            "risk_id": "FUEL-001",
            "category": "Fuel Price Volatility",
            "severity": "UNKNOWN",
            "current_value": f"KSh {tender_specs.get('diesel_price_ksh', 'N/A')}/L",
            "projected_range": "Calculation error",
            "mitigation": "Manual review required"
        })
    
    # Warranty risk
    try:
        warranty_months = tender_specs.get("warranty_months", 12)
        war_risk, war_desc = calculate_warranty_risk(warranty_months, equipment_category)
        
        risks.append({
            "risk_id": "WAR-001",
            "category": "Extended Warranty Liability",
            "severity": war_risk,
            "current_value": f"{warranty_months} months",
            "projected_range": war_desc,
            "mitigation": "Negotiate warranty backed by manufacturer, not dealer. Cap parts cost exposure."
        })
    except Exception as e:
        print(f"WARNING: Warranty risk calculation failed: {e}")
    
    # Local content risk
    try:
        local_content_pct = tender_specs.get("local_content_pct", 0)
        if local_content_pct is None:
            local_content_pct = 0
        
        local_content_pct = float(local_content_pct)
        
        if local_content_pct > 30:
            severity = "CRITICAL" if local_content_pct > 50 else "HIGH"
            risks.append({
                "risk_id": "LOC-001",
                "category": "Local Content Requirement",
                "severity": severity,
                "current_value": f"{local_content_pct:.1f}%",
                "projected_range": "LiuGong parts locally stocked: ~15-20%",
                "mitigation": "Partner with local assembly or fabrication. Document local dealer network as content."
            })
    except Exception as e:
        print(f"WARNING: Local content risk calculation failed: {e}")
    
    # Liquidated damages risk
    try:
        ld_amount = tender_specs.get("liquidated_damages_usd", 0)
        if ld_amount is None:
            ld_amount = 0
        
        ld_amount = float(ld_amount)
        
        if ld_amount > 50000:
            severity = "CRITICAL" if ld_amount > 200000 else "HIGH"
            risks.append({
                "risk_id": "LD-001",
                "category": "Liquidated Damages",
                "severity": severity,
                "current_value": f"${ld_amount:,.2f}",
                "projected_range": "Up to 10% of contract value",
                "mitigation": "Cap LD at 5% of contract. Negotiate grace period for parts delays beyond dealer control."
            })
    except Exception as e:
        print(f"WARNING: Liquidated damages risk calculation failed: {e}")
    
    # Currency fluctuation risk
    try:
        contract_currency = tender_specs.get("contract_currency", "USD")
        if contract_currency.upper() != "USD":
            risks.append({
                "risk_id": "CUR-001",
                "category": "Currency Fluctuation",
                "severity": "MEDIUM",
                "current_value": f"Contract in {contract_currency}",
                "projected_range": "KSh/USD volatility: ±15% annually",
                "mitigation": "Price in USD with local currency adjustment clause or hedge via forward contract"
            })
    except Exception as e:
        print(f"WARNING: Currency risk calculation failed: {e}")
    
    return risks

def print_risk_register(risks):
    """
    Print formatted risk register.
    Handles empty or invalid input gracefully.
    """
    print(f"\n{'='*70}")
    print("TCO RISK REGISTER")
    print(f"{'='*70}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if not risks:
        print("No risks identified.")
        print(f"{'='*70}")
        return
    
    if not isinstance(risks, list):
        print(f"ERROR: Expected list of risks, got {type(risks).__name__}")
        return
    
    # Count by severity
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    for risk in risks:
        if isinstance(risk, dict):
            severity_counts[risk.get("severity", "UNKNOWN")] = severity_counts.get(risk.get("severity", "UNKNOWN"), 0) + 1
    
    print(f"Total Risks: {len(risks)} | 🔴 {severity_counts['CRITICAL']} | 🟠 {severity_counts['HIGH']} | 🟡 {severity_counts['MEDIUM']} | 🟢 {severity_counts['LOW']} | ⚪ {severity_counts['UNKNOWN']}")
    print(f"{'='*70}")
    
    severity_icon = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢",
        "UNKNOWN": "⚪"
    }
    
    for i, risk in enumerate(risks, 1):
        if not isinstance(risk, dict):
            print(f"\nWARNING: Invalid risk entry at position {i}")
            continue
        
        sev = risk.get("severity", "UNKNOWN")
        icon = severity_icon.get(sev, "⚪")
        
        print(f"\n{i}. {risk.get('risk_id', 'N/A')} {icon} {sev}")
        print(f"   Category: {risk.get('category', 'N/A')}")
        print(f"   Current: {risk.get('current_value', 'N/A')}")
        print(f"   Projection: {risk.get('projected_range', 'N/A')}")
        print(f"   Mitigation: {risk.get('mitigation', 'N/A')}")
        print("-" * 70)

# Test with comprehensive error cases
if __name__ == "__main__":
    print("TEST 1: Normal tender")
    tender1 = {
        "diesel_price_ksh": 180,
        "warranty_months": 24,
        "local_content_pct": 40,
        "liquidated_damages_usd": 100000,
        "contract_currency": "KES"
    }
    risks1 = generate_tco_risk_register(tender1, "excavators")
    print_risk_register(risks1)
    
    print("\n\nTEST 2: Minimal tender (missing fields)")
    tender2 = {}
    risks2 = generate_tco_risk_register(tender2, "excavators")
    print_risk_register(risks2)
    
    print("\n\nTEST 3: Invalid inputs")
    tender3 = {
        "diesel_price_ksh": "invalid",
        "warranty_months": -5,
        "local_content_pct": None,
        "liquidated_damages_usd": "big"
    }
    risks3 = generate_tco_risk_register(tender3, "unknown_category")
    print_risk_register(risks3)
    
    print("\n\nTEST 4: Edge case - extreme values")
    tender4 = {
        "diesel_price_ksh": 999,
        "warranty_months": 60,
        "local_content_pct": 75,
        "liquidated_damages_usd": 500000
    }
    risks4 = generate_tco_risk_register(tender4, "wheel_loaders")
    print_risk_register(risks4)
