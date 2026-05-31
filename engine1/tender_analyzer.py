import json
import sys
from pathlib import Path

def load_profiles(filepath="data/competitor_profiles.json"):
    """
    Load competitor profiles from JSON file.
    Returns dict or None if file missing/invalid.
    """
    try:
        # Handle relative paths from different working directories
        if not Path(filepath).exists():
            # Try relative to script location
            script_dir = Path(__file__).parent.parent
            filepath = script_dir / filepath
            
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Could not find {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in {filepath}")
        return None


def score_compliance(tender_specs, product_specs):
    """
    Compare tender specs against product specs.
    Returns: score, gaps list, mitigations list
    """
    score = 0
    gaps = []
    mitigations = []
    
    for spec, required in tender_specs.items():
        actual = product_specs.get(spec)
        
        if actual is None:
            gaps.append(f"Missing: {spec}")
            mitigations.append(f"Negotiate equivalency for {spec}")
        elif actual >= required:
            score += 10
        else:
            gaps.append(f"Shortfall: {spec} (required: {required}, actual: {actual})")
            mitigations.append(f"Offer upgrade or functional equivalency for {spec}")
    
    return score, gaps, mitigations


def analyze_tender(tender_specs, equipment_category, profiles):
    """
    Analyze tender against all competitors in category.
    Returns ranked list of LiuGong alternatives.
    
    Robustness:
    - Validates category exists
    - Handles missing fields gracefully
    - Returns empty list if no data
    """
    if profiles is None:
        print("ERROR: No profiles loaded")
        return []
    
    category_data = profiles.get(equipment_category, [])
    
    if not category_data:
        print(f"WARNING: No competitors found for category '{equipment_category}'")
        return []
    
    results = []
    
    for competitor in category_data:
        # Build competitor specs dict with safe defaults
        comp_specs = {
            "engine_hp": competitor.get("engine_hp", 0),
            "operating_weight_kg": competitor.get("operating_weight_kg", 0),
            "bucket_capacity_m3": competitor.get("bucket_capacity_m3", 0),
            "price_usd": competitor.get("price_usd", 0)
        }
        
        # Run compliance check
        score, gaps, mitigations = score_compliance(tender_specs, comp_specs)
        
        results.append({
            "competitor": f"{competitor.get('competitor', 'Unknown')} {competitor.get('model', 'Unknown')}",
            "liugong_equivalent": competitor.get("liugong_equivalent", "N/A"),
            "score": score,
            "gaps": gaps,
            "mitigations": mitigations,
            "sales_pitch": competitor.get("sales_pitch", "No pitch available"),
            "price_usd": competitor.get("price_usd", 0)
        })
    
    # Sort by score descending, then by price ascending (cheaper first if tied)
    results.sort(key=lambda x: (-x["score"], x["price_usd"]))
    
    return results


def print_report(results, equipment_category, tender_specs):
    """
    Print formatted report to terminal.
    """
    print(f"\n{'='*60}")
    print(f"TENDER ANALYSIS: {equipment_category.upper()}")
    print(f"{'='*60}")
    print(f"Tender Requirements: {tender_specs}")
    print(f"Total Competitors Analyzed: {len(results)}")
    print(f"{'='*60}")
    
    if not results:
        print("No results to display.")
        return
    
    for i, r in enumerate(results, 1):
        status = "✓ COMPLIANT" if r["score"] >= 30 else "⚠ GAPS"
        print(f"\n{i}. {r['competitor']} [{status}]")
        print(f"   Score: {r['score']}/50")
        print(f"   LiuGong Alternative: {r['liugong_equivalent']}")
        print(f"   Price: ${r['price_usd']:,}")
        print(f"   Pitch: {r['sales_pitch']}")
        
        if r["gaps"]:
            print(f"   Gaps: {', '.join(r['gaps'])}")
        if r["mitigations"]:
            print(f"   Mitigations: {', '.join(r['mitigations'])}")
        print("-" * 60)
    
    # Best recommendation
    best = results[0]
    print(f"\n{'='*60}")
    print(f"RECOMMENDED: {best['liugong_equivalent']}")
    print(f"Reason: Highest compliance score ({best['score']}) with competitive pricing")
    print(f"{'='*60}")


# Test cases
if __name__ == "__main__":
    # Load profiles
    profiles = load_profiles()
    
    if profiles is None:
        sys.exit(1)
    
    # Test 1: Excavator tender requiring 180 HP
    print("\n" + "TEST 1: EXCAVATOR TENDER")
    tender_excavator = {"engine_hp": 180}
    results = analyze_tender(tender_excavator, "excavators", profiles)
    print_report(results, "excavators", tender_excavator)
    
    # Test 2: Wheel loader tender requiring 300 HP
    print("\n" + "TEST 2: WHEEL LOADER TENDER")
    tender_loader = {"engine_hp": 300}
    results = analyze_tender(tender_loader, "wheel_loaders", profiles)
    print_report(results, "wheel_loaders", tender_loader)
    
    # Test 3: Invalid category (error handling)
    print("\n" + "TEST 3: INVALID CATEGORY")
    results = analyze_tender({"engine_hp": 100}, "cranes", profiles)
    print_report(results, "cranes", {"engine_hp": 100})
