def score_compliance(tender_specs, product_specs):
  """
  Compare tender specifications against product specifications.
  Returns compliance score, gaps, and mitigation strategies.
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

# Test with LiuGong 194kw Grader vs Horn Of Africa GGP tender
if __name__ == "__main__":
  tender_grader = {
      "power_hp": 180,
      "ripper": 1,
      "scarifier": 1,
      "ac": 1,
      "fm_radio": 1,
      "reflective_chevrons": 1,
      "spare_wheel": 1
      "compressor": 1
  }
  product = {
    "power_hp": 260,
    "ripper": 1,
    "scarifier": 1,
    "ac": 1,
    "fm_radio": 1,
    "reflective_chevrons": 1,
    "spare_wheel": 1
    "compressor": 1
  }

score, gaps, mitigations = score_compliance(tender, product)
print(f"\n=== LiuGong Grader vs HOAGDP Tender ===")
print(f"Compliance Score: {score}/80")
print(f"Gaps: {gaps}")
print(f"Mitigations: {mitigattions}")
 


