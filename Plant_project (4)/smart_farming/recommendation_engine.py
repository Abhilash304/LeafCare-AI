"""
recommendation_engine.py - Smart recommendation engine based on disease detection
Provides pesticides/medicines for diseased plants, fertilizers for healthy ones
"""

# Recommendation database - expandable for more diseases
DISEASE_RECOMMENDATIONS = {
    "Leaf Blight": {
        "cause": "Fungal infection caused by Alternaria spp. Favored by warm, humid conditions.",
        "pesticide": "Copper-based fungicide (Bordeaux mixture) or Mancozeb",
        "usage": "Spray 2-3g per liter of water. Apply every 7-10 days. Avoid during flowering.",
        "preventive": "Remove infected leaves, ensure good air circulation, avoid overhead irrigation."
    },
    "Bacterial Spot": {
        "cause": "Bacterial infection (Xanthomonas spp.). Spreads through water splash and tools.",
        "pesticide": "Copper oxychloride or Streptomycin-based bactericide",
        "usage": "Apply 3g per liter. Spray every 5-7 days. Rotate with different modes of action.",
        "preventive": "Use certified disease-free seeds, sterilize tools, practice crop rotation."
    },
    "Early Blight": {
        "cause": "Fungal disease (Alternaria solani). Common in tomatoes and potatoes.",
        "pesticide": "Chlorothalonil or Azoxystrobin",
        "usage": "Mix 2ml per liter. Spray at 10-day intervals. Start before disease appears.",
        "preventive": "Mulch soil, space plants properly, remove lower infected leaves."
    },
    "Late Blight": {
        "cause": "Oomycete (Phytophthora infestans). Thrives in cool, wet weather.",
        "pesticide": "Metalaxyl + Mancozeb or Cymoxanil-based fungicide",
        "usage": "Apply as per label (typically 2-3g/L). Repeat every 7 days in wet conditions.",
        "preventive": "Avoid wetting foliage, destroy crop residue, use resistant varieties."
    },
    "Powdery Mildew": {
        "cause": "Fungal infection (Erysiphe spp.). Favored by dry foliage and high humidity at night.",
        "pesticide": "Sulfur dust or Potassium bicarbonate",
        "usage": "Sulfur: dust lightly on leaves. Bicarbonate: 5g per liter, spray weekly.",
        "preventive": "Improve air flow, reduce nitrogen, water at base of plant."
    },
    "Leaf Spot": {
        "cause": "Various fungal or bacterial pathogens causing circular spots on leaves.",
        "pesticide": "Mancozeb or Copper-based fungicide",
        "usage": "Spray 2g per liter every 7-10 days until condition improves.",
        "preventive": "Remove infected leaves, avoid overhead watering, ensure drainage."
    },
}

# Fertilizer recommendations for healthy plants
HEALTHY_PLANT_RECOMMENDATIONS = [
    {
        "fertilizer": "NPK 19:19:19",
        "quantity": "25 kg/acre",
        "when": "During vegetative growth stage",
        "tips": "Apply in split doses. Ensure adequate irrigation after application."
    },
    {
        "fertilizer": "Urea",
        "quantity": "20 kg/acre",
        "when": "For nitrogen boost in early growth",
        "tips": "Mix with soil or apply as top dressing. Avoid direct contact with leaves."
    },
    {
        "fertilizer": "DAP (Di-Ammonium Phosphate)",
        "quantity": "50 kg/acre",
        "when": "At sowing or transplanting",
        "tips": "Place 5-7 cm below seed. Promotes strong root development."
    },
    {
        "fertilizer": "Potash (MOP)",
        "quantity": "30 kg/acre",
        "when": "During flowering and fruiting",
        "tips": "Improves disease resistance and fruit quality. Apply with irrigation."
    },
    {
        "fertilizer": "Organic Compost",
        "quantity": "2-3 tonnes/acre",
        "when": "Before planting or as top dressing",
        "tips": "Improves soil structure and microbial activity. Apply annually."
    },
]


def get_recommendation(disease_name, health_status):
    """
    Get smart recommendation based on disease detection result
    Returns dict with appropriate fields for UI display
    """
    if health_status == "Healthy":
        # Return fertilizer recommendation for healthy plants
        import random
        rec = random.choice(HEALTHY_PLANT_RECOMMENDATIONS)
        return {
            "type": "healthy",
            "fertilizer": rec["fertilizer"],
            "quantity": rec["quantity"],
            "when_to_apply": rec["when"],
            "preventive_tips": [
                "Monitor plants regularly for early signs of disease.",
                "Practice crop rotation to reduce soil-borne pathogens.",
                "Maintain proper spacing for air circulation.",
                "Use mulch to reduce soil splash and weed competition.",
                "Ensure balanced nutrition - avoid excess nitrogen."
            ],
            "cause": None,
            "pesticide": None,
            "usage": None
        }

    # Diseased - look up recommendation
    disease_key = disease_name
    if disease_key not in DISEASE_RECOMMENDATIONS:
        # Generic recommendation for unknown disease
        disease_key = "Leaf Spot"  # Use as default

    rec = DISEASE_RECOMMENDATIONS.get(disease_key, DISEASE_RECOMMENDATIONS["Leaf Spot"])

    return {
        "type": "diseased",
        "cause": rec["cause"],
        "pesticide": rec["pesticide"],
        "usage": rec["usage"],
        "preventive_tips": [rec["preventive"]],
        "fertilizer": None,
        "quantity": None,
        "when_to_apply": None
    }
