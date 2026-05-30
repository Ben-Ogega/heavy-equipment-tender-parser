import json

def load_competitor_profiles(filepath="data/competitor_profiles.json"):
  """
  Load competitor profiles from JSON file.

  """
  with open(filepath, "r") as f:
    return json.load(f)

def find_competitors_gap(tender_specs, equipment_category, competitor_name, profiles):
  """
  Compare tender specs against a specific competitor's product
  Returns: Competitor specs, LiuGong equivalent, gap analysis
  """
  category_data = profiles.get(equipment_category, [])
  competitor = None
  for item in category_data:
    if item["competitor"] == competitor_name:
      competitor = item
      break

    if not competitor:
      return None, None, f"Competitor {competitor_name} not found"

# Extract relevant specs for comparison
  competitor_specs = {
    "engine_hp": competitor.get("liugong-equivalent")
    "price_usd": competitor.get("sales_pitch")

# Run compliance check
  score, gaps, mitigations = score_compliance(tender_specs, competitor_specs)
  return {
          "competitor": competitor,
          "liugong_equivalent": liugong_equipment,
          "compliance_score": score,
          "gaps": gaps,
          "mitigations": mitigations
  }

# Test: Compare CAT 320 against tender requiring 180HP excavator

if __name__ == "__main__":
  profiles = load_competitor_profiles()
  tender = {
            "engine_hp": 180, 
            "bucket_capacity_m3": 1.0
  }

result = find_competitor_gaps(tender, "excavators", "CAT", profiles)
print(f"CAT 320 vs Tender: score(result['compliance_score']}")
print(f"LiuGong Alternative: {result['liugomg-equivalent']}")
print(f"Sales pitch: {result['sales_pitch']}")
  
