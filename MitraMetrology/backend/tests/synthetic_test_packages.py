"""
Synthetic test packages for comprehensive Phase 2 testing
Represents realistic but fictional packaged commodities for testing compliance scenarios
"""

COMPLIANT_PACKAGE = {
    """
    Well-labeled package with all required declarations
    Suitable for testing successful compliance scenarios
    """
    "product_name": "Premium Tea - Assorted",
    "manufacturer": "Chai Enterprises Ltd., 42 Tea Street, Delhi, India",
    "packer": "Chai Enterprises Ltd.",
    "importer": None,
    "net_quantity": "500g",
    "mrp": "₹299",
    "consumer_care": "Store in a cool, dry place. Keep away from moisture.",
    "mfg_date": "01/08/2026",
    "images": [
        {
            "name": "compliant_front.jpg",
            "ocr_text": """
                PREMIUM TEA ASSORTED
                Maximum Retail Price: ₹299
                Net weight: 500g
                Manufactured by: Chai Enterprises Ltd.
                42 Tea Street, Delhi, India
                Best before: 01/02/2027
                Consumer Care: Store in cool, dry place
                """,
            "fields": {
                "product_name": "PREMIUM TEA ASSORTED",
                "mrp": "₹299",
                "net_quantity": "500g",
                "manufacturer": "Chai Enterprises Ltd."
            }
        }
    ]
}

MISSING_MRP_PACKAGE = {
    """
    Package missing MRP declaration - should be flagged as non-compliant
    """
    "product_name": "Biscuits - Digestive",
    "manufacturer": "Baked Goods Inc., Mumbai",
    "packer": "Baked Goods Inc.",
    "net_quantity": "250g",
    "mrp": None,  # MISSING - Critical violation
    "consumer_care": "Consume within expiry date",
    "images": [
        {
            "name": "missing_mrp_front.jpg",
            "ocr_text": """
                DIGESTIVE BISCUITS
                Net Weight: 250g
                Manufacturer: Baked Goods Inc., Mumbai
                Best Before: 01/12/2026
                """,
            "fields": {
                "product_name": "DIGESTIVE BISCUITS",
                "net_quantity": "250g",
                "manufacturer": "Baked Goods Inc.",
                "mrp": None
            }
        }
    ]
}

MISSING_MANUFACTURER_PACKAGE = {
    """
    Package missing manufacturer details - critical violation
    """
    "product_name": "Energy Drink",
    "manufacturer": None,  # MISSING - Critical violation
    "net_quantity": "250ml",
    "mrp": "₹80",
    "consumer_care": "Keep refrigerated after opening",
    "images": [
        {
            "name": "missing_mfg.jpg",
            "ocr_text": """
                POWER BOOST ENERGY DRINK
                MRP: ₹80
                Net Volume: 250ml
                Best Before: 01/11/2026
                """,
            "fields": {
                "product_name": "POWER BOOST",
                "mrp": "₹80",
                "net_quantity": "250ml",
                "manufacturer": None
            }
        }
    ]
}

CONFLICTING_VALUES_PACKAGE = {
    """
    Package with conflicting values across images (e.g., different front/back)
    """
    "product_name": "Cooking Oil",
    "manufacturer": "Oil Refineries Ltd., Gujarat",
    "net_quantity": "1L",
    "mrp": "₹150 (front) vs ₹160 (back)",  # CONFLICT
    "images": [
        {
            "name": "oil_front.jpg",
            "ocr_text": """
                PURE COOKING OIL
                MRP: ₹150
                Volume: 1 Liter
                Manufacturer: Oil Refineries Ltd.
                """,
            "fields": {
                "mrp": "₹150",
                "net_quantity": "1L"
            }
        },
        {
            "name": "oil_back.jpg",
            "ocr_text": """
                Net Volume: 1L
                Maximum Retail Price: ₹160
                """,
            "fields": {
                "mrp": "₹160",
                "net_quantity": "1L"
            }
        }
    ]
}

BLURRY_IMAGE_PACKAGE = {
    """
    Package with poor image quality - readability issues
    Should trigger readability warnings
    """
    "product_name": "Coffee",
    "manufacturer": "Coffee Estates",
    "net_quantity": "100g",
    "mrp": "₹250",
    "images": [
        {
            "name": "blurry_image.jpg",
            "ocr_text": """
                [Blurry/Low contrast]
                Coffee ... Estates
                ... g
                MRP ... 250
                """,
            "readability_issues": [
                "Image is blurry",
                "Low contrast detected",
                "Text may be hard to read"
            ],
            "readability_score": 35
        }
    ]
}

HINDI_ENGLISH_MIX_PACKAGE = {
    """
    Package with Hindi and English mixed - should handle both languages
    """
    "product_name": "Spice Mix - मसाला",
    "manufacturer": "भारतीय मसाले कंपनी / Indian Spices Co.",
    "net_quantity": "100g / 100 ग्राम",
    "mrp": "₹99",
    "images": [
        {
            "name": "bilingual_package.jpg",
            "ocr_text": """
                भारतीय मसाला
                Indian Spice Mix
                MRP / कीमत: ₹99
                Net Weight / वजन: 100g
                Manufacturer / निर्माता: Indian Spices Co.
                """,
            "fields": {
                "product_name": "भारतीय मसाला / Indian Spice Mix",
                "mrp": "₹99",
                "net_quantity": "100g",
                "manufacturer": "Indian Spices Co."
            }
        }
    ]
}

INCORRECT_FORMAT_PACKAGE = {
    """
    Package with incorrect quantity format or unclear MRP
    """
    "product_name": "Milk Powder",
    "manufacturer": "Dairy Ltd",
    "net_quantity": "approx 400g",  # Vague - should be exact
    "mrp": "₹450-500",  # Range instead of exact price
    "images": [
        {
            "name": "incorrect_format.jpg",
            "ocr_text": """
                MILK POWDER
                MRP: ₹450 - ₹500
                Net Weight: Approximately 400g
                Manufacturer: Dairy Ltd
                """,
            "fields": {
                "net_quantity": "approx 400g",
                "mrp": "₹450-500"
            },
            "warnings": [
                "MRP should be single value, not range",
                "Net quantity should be exact, not approximate"
            ]
        }
    ]
}

ROTATED_IMAGE_PACKAGE = {
    """
    Package with image requiring rotation correction
    """
    "product_name": "Chocolate",
    "images": [
        {
            "name": "rotated_image.jpg",
            "rotation_angle": 90,  # Needs rotation
            "note": "Image should be rotated for proper OCR"
        }
    ]
}

DUPLICATE_IMAGE_PACKAGE = {
    """
    Package with duplicate/very similar images
    Should be detected and flagged
    """
    "product_name": "Cereal",
    "images": [
        {
            "name": "cereal_image_1.jpg",
            "ocr_text": "BREAKFAST CEREAL MRP ₹150 500g"
        },
        {
            "name": "cereal_image_2.jpg",
            "ocr_text": "BREAKFAST CEREAL MRP ₹150 500g",
            "note": "Nearly identical to image_1"
        }
    ]
}

MULTIPLE_IMAGES_CONSISTENT_PACKAGE = {
    """
    Package with multiple images (front, back, side) all consistent
    """
    "product_name": "Soap Bar",
    "images": [
        {
            "name": "soap_front.jpg",
            "ocr_text": """
                PREMIUM SOAP
                MRP: ₹50
                Net Weight: 100g
                """,
            "image_type": "front"
        },
        {
            "name": "soap_back.jpg",
            "ocr_text": """
                Ingredients: Coconut Oil, Palm Oil
                Manufacturer: Soap Co. Ltd.
                """,
            "image_type": "back"
        },
        {
            "name": "soap_side.jpg",
            "ocr_text": """
                MRP ₹50
                100g Net Weight
                """,
            "image_type": "side"
        }
    ]
}

POOR_LIGHTING_PACKAGE = {
    """
    Package photographed in poor lighting conditions
    Should trigger readability warnings
    """
    "product_name": "Juice",
    "images": [
        {
            "name": "poorly_lit.jpg",
            "ocr_text": "[Faint/Hard to read text due to poor lighting]",
            "brightness": 40,  # Very low brightness
            "contrast": 25,    # Very low contrast
            "readability_score": 25,
            "issues": [
                "Image too dark",
                "Low contrast",
                "Text barely visible"
            ]
        }
    ]
}

# Test scenarios mapping
TEST_SCENARIOS = {
    "compliant": COMPLIANT_PACKAGE,
    "missing_mrp": MISSING_MRP_PACKAGE,
    "missing_manufacturer": MISSING_MANUFACTURER_PACKAGE,
    "conflicting_values": CONFLICTING_VALUES_PACKAGE,
    "blurry_image": BLURRY_IMAGE_PACKAGE,
    "hindi_english_mix": HINDI_ENGLISH_MIX_PACKAGE,
    "incorrect_format": INCORRECT_FORMAT_PACKAGE,
    "rotated_image": ROTATED_IMAGE_PACKAGE,
    "duplicate_images": DUPLICATE_IMAGE_PACKAGE,
    "multiple_consistent": MULTIPLE_IMAGES_CONSISTENT_PACKAGE,
    "poor_lighting": POOR_LIGHTING_PACKAGE
}


def get_test_package(scenario_name: str) -> dict:
    """Retrieve a test package by scenario name"""
    return TEST_SCENARIOS.get(scenario_name)


def list_test_scenarios() -> list:
    """List all available test scenarios"""
    return list(TEST_SCENARIOS.keys())


def get_test_scenario_description(scenario_name: str) -> str:
    """Get description of a test scenario"""
    if scenario_name not in TEST_SCENARIOS:
        return "Unknown scenario"
    
    doc = TEST_SCENARIOS[scenario_name].__doc__
    return doc.strip() if doc else "No description available"
