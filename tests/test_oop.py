import sys
sys.path.append('..')

from engine1.compliance_oop import Spec, CompetitorSpec, TenderSpec, ComplianceAnalyzer
import json

# Load data
with open("data/competitor_profiles.json") as f:
    profiles = json.load(f)

with open("data/tender_specs.json") as f:
    tender_data = json.load(f)

# Test 1: LiuGong 922E vs CAT 320
print("=" * 50)
print("TEST 1: LiuGong 922E vs CAT 320")
print("=" * 50)

liugong_922e = {
    "competitor": "LiuGong",
    "model": "922E",
    "engine_hp": 162,
    "operating_weight_kg": 21500,
    "bucket_capacity_m3": 1.19,
    "price_usd": 120000
}

cat_320 = CompetitorSpec(profiles['excavators'][0])
product = Spec(liugong_922e)
analyzer = ComplianceAnalyzer(product)
result = analyzer.analyze(cat_320)

print(f"Score: {result['score']}/{result['max_score']} ({result['percentage']:.1f}%)")
print(f"Gaps: {result['gaps']}")
print(f"Compliant: {result['compliant']}")

# Test 2: LiuGong 922E vs Tender MoR&T/SDoR/ONT/01/2024-2025
print("\n" + "=" * 50)
print("TEST 2: LiuGong 922E vs Tender")
print("=" * 50)

tender = TenderSpec(tender_data['tender_specs'])
result = analyzer.analyze(tender)

print(f"Score: {result['score']}/{result['max_score']} ({result['percentage']:.1f}%)")
print(f"Gaps: {result['gaps']}")
print(f"Compliant: {result['compliant']}")

# Test 3: LiuGong 936E (hypothetical) vs Tender
print("\n" + "=" * 50)
print("TEST 3: LiuGong 936E vs Tender")
print("=" * 50)

liugong_936e = {
    "competitor": "LiuGong",
    "model": "936E",
    "engine_hp": 220,
    "operating_weight_kg": 33000,
    "bucket_capacity_m3": 1.5,
    "price_usd": 150000,
    "technology": {
        "avm_around_view_monitor": True,
        "fleet_management_system": True,
        "spc_smart_power_control": True,
        "side_rear_cameras": True,
        "centralized_grease_inlets": True
    },
    "warranty_hours": 2000
}

product = Spec(liugong_936e)
analyzer = ComplianceAnalyzer(product)
result = analyzer.analyze(tender)

print(f"Score: {result['score']}/{result['max_score']} ({result['percentage']:.1f}%)")
print(f"Gaps: {result['gaps']}")
print(f"Compliant: {result['compliant']}")
