"""
Test script to demonstrate the improved scoring system
"""

from scoreCalculator import score_calculator

# Test preferences
test_preferences = {
    "flat_type": "4 ROOM",
    "storey_range": "07 TO 09",
    "floor_area_sqm": "91-110",
    "flat_model": "Improved",
    "price_range": "400k-500k"
}

# Test flats with varying degrees of match
test_flats = [
    {
        "name": "Perfect Match",
        "flat_type": "4 ROOM",
        "storey_range": "07 TO 09",
        "floor_area_sqm": 95,
        "flat_model": "Improved",
        "resale_price": 450000
    },
    {
        "name": "Very Close Match (Adjacent Room Type)",
        "flat_type": "3 ROOM",
        "storey_range": "07 TO 09",
        "floor_area_sqm": 92,
        "flat_model": "Improved",
        "resale_price": 440000
    },
    {
        "name": "Close Match (Adjacent Floor)",
        "flat_type": "4 ROOM",
        "storey_range": "10 TO 12",
        "floor_area_sqm": 98,
        "flat_model": "Improved",
        "resale_price": 460000
    },
    {
        "name": "Good Match (Similar Area)",
        "flat_type": "4 ROOM",
        "storey_range": "07 TO 09",
        "floor_area_sqm": 85,
        "flat_model": "Standard",
        "resale_price": 430000
    },
    {
        "name": "Fair Match (Different Size)",
        "flat_type": "4 ROOM",
        "storey_range": "13 TO 15",
        "floor_area_sqm": 70,
        "flat_model": "Improved",
        "resale_price": 420000
    },
    {
        "name": "Poor Match (Multiple Differences)",
        "flat_type": "2 ROOM",
        "storey_range": "19 TO 21",
        "floor_area_sqm": 55,
        "flat_model": "Standard",
        "resale_price": 350000
    },
    {
        "name": "Over Budget",
        "flat_type": "4 ROOM",
        "storey_range": "07 TO 09",
        "floor_area_sqm": 95,
        "flat_model": "Improved",
        "resale_price": 550000
    },
    {
        "name": "Under Budget (Good Deal)",
        "flat_type": "4 ROOM",
        "storey_range": "04 TO 06",
        "floor_area_sqm": 88,
        "flat_model": "Standard",
        "resale_price": 380000
    }
]

print("=" * 80)
print("IMPROVED SCORING SYSTEM DEMONSTRATION")
print("=" * 80)
print("\nUser Preferences:")
print(f"  Flat Type: {test_preferences['flat_type']}")
print(f"  Storey Range: {test_preferences['storey_range']}")
print(f"  Floor Area: {test_preferences['floor_area_sqm']} sqm")
print(f"  Flat Model: {test_preferences['flat_model']}")
print(f"  Price Range: {test_preferences['price_range']}")
print("\n" + "=" * 80)

# Test each flat
for flat in test_flats:
    print(f"\n{flat['name']}")
    print("-" * 80)
    
    # Calculate overall score
    score = score_calculator.calculate_score(flat, test_preferences)
    
    # Get detailed breakdown
    breakdown = score_calculator.get_score_breakdown(flat, test_preferences)
    
    # Display flat details
    print(f"Flat Details:")
    print(f"  Type: {flat['flat_type']}, Floor: {flat['storey_range']}, " 
          f"Area: {flat['floor_area_sqm']}m², Model: {flat['flat_model']}, "
          f"Price: ${flat['resale_price']:,}")
    
    print(f"\nOverall Compatibility Score: {score}%")
    
    # Display breakdown
    print(f"\nDetailed Breakdown:")
    for criterion, details in breakdown.items():
        criterion_name = criterion.replace('_', ' ').title()
        print(f"  {criterion_name}:")
        print(f"    Preference: {details['preference']}, Actual: {details['actual']}")
        print(f"    Score: {details['score']}% (Weight: {details['weight']*100}%) "
              f"→ Contribution: {details['weighted_score']}%")
        print(f"    Match Quality: {details['match_quality']}")

print("\n" + "=" * 80)
print("SCORING IMPROVEMENTS:")
print("=" * 80)
print("""
1. Flat Type: Now considers room count similarity with smooth scoring
   - Adjacent room types get 60% score (e.g., 3-room vs 4-room)
   - 2 rooms difference get 30% score
   - Larger differences get 10% score

2. Storey Range: Uses floor proximity with exponential decay
   - Same or adjacent ranges: 85% score
   - 1 range away (3-6 floors): 60% score
   - 2 ranges away (6-9 floors): 35% score
   - Gradual decay for larger differences

3. Floor Area: Gaussian-like decay from center of preferred range
   - Full score within range, slight preference for center
   - Smooth decay outside range based on distance
   - More tolerance for nearby sizes

4. Price Range: Budget-sensitive scoring with asymmetric decay
   - Lower prices than budget: high scores (cheaper is better)
   - Higher prices: steeper penalty (over budget is worse)
   - Smooth transitions between categories

5. Flat Model: Category-based similarity matching
   - Same category: 75% score
   - Similar categories (Premium/Improved): 50% score
   - Partial string matches: 60% score

All criteria now provide smooth, continuous scores that reflect
the degree of match, rather than binary yes/no decisions.
""")
print("=" * 80)
