class Spec:
    """Base class for any specification set."""
    def __init__(self, specs_dict):
        self.specs = specs_dict
    
    def get(self, key, default=None):
        return self.specs.get(key, default)


class CompetitorSpec(Spec):
    """Competitor product specifications."""
    def __init__(self, specs_dict):
        super().__init__(specs_dict)
        self.name = f"{specs_dict.get('competitor', 'Unknown')} {specs_dict.get('model', 'Unknown')}"
        self.liugong_equivalent = specs_dict.get('liugong_equivalent', 'N/A')
        self.sales_pitch = specs_dict.get('sales_pitch', '')
        self.price_usd = specs_dict.get('price_usd', 0)


class TenderSpec(Spec):
    """Tender requirements."""
    def __init__(self, specs_dict):
        super().__init__(specs_dict)
        self.tender_id = specs_dict.get('tender_id', 'Unknown')
        self.lot = specs_dict.get('lot', 0)
        self.description = specs_dict.get('description', '')


class ComplianceAnalyzer:
    """
    Analyzes compliance of any product spec against any requirement spec.
    Accepts either CompetitorSpec or TenderSpec as the requirement.
    """
    
    def __init__(self, product_spec):
        self.product = product_spec
    
    def analyze(self, requirement_spec):
        """
        requirement_spec: CompetitorSpec or TenderSpec
        Returns compliance report.
        """
        score = 0
        max_score = 0
        gaps = []
        compliant = []
        
        # Common checks regardless of spec type
        max_score, score, gaps, compliant = self._check_power(
            requirement_spec, max_score, score, gaps, compliant
        )
        
        max_score, score, gaps, compliant = self._check_weight(
            requirement_spec, max_score, score, gaps, compliant
        )
        
        max_score, score, gaps, compliant = self._check_bucket(
            requirement_spec, max_score, score, gaps, compliant
        )
        
        # Tender-specific checks
        if isinstance(requirement_spec, TenderSpec):
            max_score, score, gaps, compliant = self._check_tender_specific(
                requirement_spec, max_score, score, gaps, compliant
            )
        
        return {
            "product": self.product.get('competitor', 'Unknown') + ' ' + self.product.get('model', 'Unknown'),
            "requirement": requirement_spec.name if isinstance(requirement_spec, CompetitorSpec) else requirement_spec.tender_id,
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score * 100) if max_score > 0 else 0,
            "compliant": compliant,
            "gaps": gaps
        }
    
    def _check_power(self, req, max_score, score, gaps, compliant):
        req_power = req.get('power_hp', req.get('power_hp_min', 0))
        product_power = self.product.get('engine_hp', 0)
        
        max_score += 20
        if product_power >= req_power:
            score += 20
            compliant.append(f"Power: {product_power} HP >= {req_power} HP")
        else:
            gaps.append(f"Power: {product_power} HP < {req_power} HP required")
        
        return max_score, score, gaps, compliant
    
    def _check_weight(self, req, max_score, score, gaps, compliant):
        req_weight = req.get('operating_weight_kg', 0)
        product_weight = self.product.get('operating_weight_kg', 0)
        
        max_score += 15
        if product_weight >= req_weight:
            score += 15
            compliant.append(f"Weight: {product_weight} kg >= {req_weight} kg")
        else:
            gaps.append(f"Weight: {product_weight} kg < {req_weight} kg required")
        
        return max_score, score, gaps, compliant
    
    def _check_bucket(self, req, max_score, score, gaps, compliant):
        req_bucket = req.get('bucket_capacity_m3', 0)
        product_bucket = self.product.get('bucket_capacity_m3', 0)
        
        max_score += 15
        if product_bucket >= req_bucket:
            score += 15
            compliant.append(f"Bucket: {product_bucket} m³ >= {req_bucket} m³")
        else:
            gaps.append(f"Bucket: {product_bucket} m³ < {req_bucket} m³ required")
        
        return max_score, score, gaps, compliant
    
    def _check_tender_specific(self, req, max_score, score, gaps, compliant):
        """Additional checks only for tender specs."""
        # Technology requirements
        tech_items = req.get('technology', {})
        for item, required in tech_items.items():
            max_score += 5
            if self.product.get('technology', {}).get(item, False):
                score += 5
                compliant.append(f"{item}: Present")
            else:
                gaps.append(f"{item}: Missing (required)")
        
        # Warranty
        req_warranty_hours = req.get('warranty', {}).get('hours', 0)
        product_warranty = self.product.get('warranty_hours', 0)
        
        max_score += 10
        if product_warranty >= req_warranty_hours:
            score += 10
            compliant.append(f"Warranty: {product_warranty} hrs >= {req_warranty_hours} hrs")
        else:
            gaps.append(f"Warranty: {product_warranty} hrs < {req_warranty_hours} hrs required")
        
        return max_score, score, gaps, compliant


# Usage examples
if __name__ == "__main__":
    # Load your data
    import json
    
    with open("data/competitor_profiles.json") as f:
        profiles = json.load(f)
    
    with open("data/tender_specs.json") as f:
        tender_data = json.load(f)
    
    # Example 1: Compare LiuGong against competitor
    liugong_922e = {
        "competitor": "LiuGong",
        "model": "922E",
        "engine_hp": 162,
        "operating_weight_kg": 21500,
        "bucket_capacity_m3": 1.19
    }
    
    cat_320 = CompetitorSpec(profiles['excavators'][0])
    product = Spec(liugong_922e)
    analyzer = ComplianceAnalyzer(product)
    result = analyzer.analyze(cat_320)
    print("vs CAT 320:", result)
    
    # Example 2: Compare LiuGong against tender
    tender = TenderSpec(tender_data['tender_specs'])
    result = analyzer.analyze(tender)
    print("vs Tender:", result)
