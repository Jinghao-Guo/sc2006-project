"""
Score calculation module for HDB flats based on user preferences.
The score is calculated on a scale of 0-100, where 100 means perfect match.
"""


class ScoreCalculator:
    """Calculate compatibility scores between flats and user preferences"""

    def __init__(self):
        # Adjusted weights to reflect importance of each criterion
        self.weights = {
            "flat_type": 0.25,      # Room count is very important
            "price_range": 0.25,    # Budget is crucial
            "floor_area_sqm": 0.20, # Size matters
            "storey_range": 0.15,   # Floor preference is moderate
            "flat_model": 0.15,     # Model is less critical
        }

    def calculate_score(self, flat, preferences):
        """
        Calculate the compatibility score between a flat and user preferences.

        Args:
            flat: Database row object containing flat information
            preferences: Dictionary with user preferences

        Returns:
            int: Score from 0-100 where 100 is perfect match
        """
        if not self._has_valid_preferences(preferences):
            return 0  # No preferences set, no meaningful score

        total_score = 0
        active_weights = 0

        # Calculate score for each preference criterion
        for criterion, weight in self.weights.items():
            pref_value = preferences.get(criterion, "")
            if pref_value:  # Only calculate if preference is set
                score = self._calculate_criterion_score(criterion, flat, pref_value)
                total_score += score * weight
                active_weights += weight

        # Normalize score based on active preferences only
        if active_weights > 0:
            normalized_score = (total_score / active_weights) * 100
            return round(normalized_score)

        return 0

    def _has_valid_preferences(self, preferences):
        """Check if any meaningful preferences are set"""
        return any(preferences.get(key, "") for key in self.weights.keys())

    def _calculate_criterion_score(self, criterion, flat, preference):
        """Calculate score for a specific criterion"""
        if criterion == "flat_type":
            return self._score_flat_type(flat.get("flat_type", ""), preference)
        elif criterion == "storey_range":
            return self._score_storey_range(flat.get("storey_range", ""), preference)
        elif criterion == "floor_area_sqm":
            return self._score_floor_area(flat.get("floor_area_sqm", 0), preference)
        elif criterion == "flat_model":
            return self._score_flat_model(flat.get("flat_model", ""), preference)
        elif criterion == "price_range":
            return self._score_price_range(flat.get("resale_price", 0), preference)

        return 0

    def _score_flat_type(self, flat_type, preference):
        """Score flat type match with smooth scoring based on room count similarity"""
        if not flat_type or not preference:
            return 0
        
        # Extract room counts for comparison
        flat_rooms = self._extract_room_count(flat_type)
        pref_rooms = self._extract_room_count(preference)
        
        if flat_rooms is None or pref_rooms is None:
            # Fallback to exact match for non-standard types
            return 1.0 if flat_type.upper() == preference.upper() else 0.0
        
        # Calculate score based on room count difference
        # Perfect match = 1.0, 1 room difference = 0.6, 2 rooms = 0.3, 3+ = 0.1
        room_diff = abs(flat_rooms - pref_rooms)
        if room_diff == 0:
            return 1.0
        elif room_diff == 1:
            return 0.6
        elif room_diff == 2:
            return 0.3
        else:
            return 0.1
    
    def _extract_room_count(self, flat_type):
        """Extract room count from flat type string"""
        flat_type_upper = flat_type.upper().strip()
        
        # Map flat types to room counts
        room_mapping = {
            '1 ROOM': 1,
            '2 ROOM': 2,
            '3 ROOM': 3,
            '4 ROOM': 4,
            '5 ROOM': 5,
            'EXECUTIVE': 6,  # Treat executive as 6-room equivalent
            'MULTI-GENERATION': 6,
        }
        
        return room_mapping.get(flat_type_upper)

    def _score_storey_range(self, storey_range, preference):
        """Score storey range match with smooth scoring based on floor proximity"""
        if not storey_range or not preference:
            return 0
        
        # Extract middle floor number from range
        flat_mid_floor = self._extract_mid_floor(storey_range)
        pref_mid_floor = self._extract_mid_floor(preference)
        
        if flat_mid_floor is None or pref_mid_floor is None:
            # Fallback to exact match
            return 1.0 if storey_range.upper() == preference.upper() else 0.0
        
        # Calculate score based on floor difference
        # Use exponential decay for smooth scoring
        floor_diff = abs(flat_mid_floor - pref_mid_floor)
        
        if floor_diff == 0:
            return 1.0
        elif floor_diff <= 3:
            # Same range or adjacent range
            return 0.85
        elif floor_diff <= 6:
            # One range away
            return 0.6
        elif floor_diff <= 9:
            # Two ranges away
            return 0.35
        elif floor_diff <= 12:
            # Three ranges away
            return 0.15
        else:
            # Very far away
            return 0.05
    
    def _extract_mid_floor(self, storey_range):
        """Extract middle floor number from storey range string"""
        try:
            # Parse format like "01 TO 03" or "10 TO 12"
            parts = storey_range.upper().replace("TO", " ").split()
            numbers = [int(p) for p in parts if p.isdigit()]
            if len(numbers) >= 2:
                return (numbers[0] + numbers[1]) / 2
        except (ValueError, AttributeError):
            pass
        return None

    def _score_floor_area(self, floor_area, preference):
        """Score floor area based on preference range with smooth Gaussian-like decay"""
        if not floor_area or not preference:
            return 0

        try:
            floor_area = float(floor_area)
        except (ValueError, TypeError):
            return 0

        # Parse preference ranges and get center point
        range_info = self._parse_area_preference(preference)
        if not range_info:
            return 0
        
        min_range, max_range = range_info
        center = (min_range + max_range) / 2
        range_size = max_range - min_range
        
        # Calculate distance from center of preferred range
        distance = abs(floor_area - center)
        
        # Within range: full score
        if min_range <= floor_area <= max_range:
            # Slight preference for values closer to center even within range
            normalized_distance = distance / (range_size / 2)
            return 1.0 - (normalized_distance * 0.1)  # Max 10% reduction at edges
        
        # Outside range: exponential decay based on distance
        # Use a smoother decay function
        if distance <= range_size:
            # Close to range: high score
            return 0.7 + 0.3 * (1 - distance / range_size)
        elif distance <= range_size * 2:
            # Moderately far: medium score
            normalized_dist = (distance - range_size) / range_size
            return 0.4 + 0.3 * (1 - normalized_dist)
        elif distance <= range_size * 3:
            # Far: low score
            normalized_dist = (distance - range_size * 2) / range_size
            return 0.15 + 0.25 * (1 - normalized_dist)
        else:
            # Very far: minimal score
            return max(0.05, 0.15 * (1 - min(distance / (range_size * 5), 1)))
    
    def _parse_area_preference(self, preference):
        """Parse area preference string and return (min, max) tuple"""
        area_ranges = {
            "30-50": (30, 50),
            "51-70": (51, 70),
            "71-90": (71, 90),
            "91-110": (91, 110),
            "111-130": (111, 130),
            "131-150": (131, 150),
            "151+": (151, 200),  # Assume max of 200 for open-ended range
        }
        return area_ranges.get(preference)

    def _score_flat_model(self, flat_model, preference):
        """Score flat model match with similarity scoring"""
        if not flat_model or not preference:
            return 0
        
        flat_model_upper = flat_model.upper().strip()
        preference_upper = preference.upper().strip()
        
        # Exact match
        if flat_model_upper == preference_upper:
            return 1.0
        
        # Define model categories and their similarity
        model_categories = {
            'premium': ['PREMIUM APARTMENT', 'DBSS', 'PREMIUM MAISONETTE'],
            'improved': ['IMPROVED', 'IMPROVED-MAISONETTE', 'NEW GENERATION'],
            'standard': ['STANDARD', 'MODEL A', 'MODEL A2', 'SIMPLIFIED'],
            'special': ['MAISONETTE', 'APARTMENT', 'TERRACE', 'PREMIUM APARTMENT LOFT'],
        }
        
        # Find categories for both models
        flat_category = None
        pref_category = None
        
        for category, models in model_categories.items():
            if any(model in flat_model_upper for model in models):
                flat_category = category
            if any(model in preference_upper for model in models):
                pref_category = category
        
        # Same category: good match
        if flat_category and pref_category and flat_category == pref_category:
            return 0.75
        
        # Different but known categories: partial match
        if flat_category and pref_category:
            # Premium and improved are somewhat similar
            if (flat_category == 'premium' and pref_category == 'improved') or \
               (flat_category == 'improved' and pref_category == 'premium'):
                return 0.5
            # Standard and improved are somewhat similar
            elif (flat_category == 'standard' and pref_category == 'improved') or \
                 (flat_category == 'improved' and pref_category == 'standard'):
                return 0.4
            else:
                return 0.2
        
        # Partial string match as fallback
        if preference_upper in flat_model_upper or flat_model_upper in preference_upper:
            return 0.6
        
        # No match
        return 0.1

    def _score_price_range(self, price, preference):
        """Score price based on preference range with smooth decay and budget sensitivity"""
        if not price or not preference:
            return 0

        try:
            price = float(price)
        except (ValueError, TypeError):
            return 0

        # Parse preference ranges
        range_info = self._parse_price_preference(preference)
        if not range_info:
            return 0
        
        min_range, max_range = range_info
        center = (min_range + max_range) / 2
        range_size = max_range - min_range
        
        # Within range: excellent score with slight preference for lower prices
        if min_range <= price <= max_range:
            # Normalize position within range (0 = min, 1 = max)
            position = (price - min_range) / range_size if range_size > 0 else 0
            # Slight preference for lower prices: 1.0 at min, 0.95 at max
            return 1.0 - (position * 0.05)
        
        # Below range: still good (cheaper is usually better)
        if price < min_range:
            distance = min_range - price
            # More tolerance for lower prices
            if distance <= range_size * 0.5:
                return 0.85 + 0.15 * (1 - distance / (range_size * 0.5))
            elif distance <= range_size:
                return 0.65 + 0.20 * (1 - (distance - range_size * 0.5) / (range_size * 0.5))
            elif distance <= range_size * 2:
                normalized_dist = (distance - range_size) / range_size
                return 0.35 + 0.30 * (1 - normalized_dist)
            else:
                return max(0.1, 0.35 * (1 - min(distance / (range_size * 4), 1)))
        
        # Above range: worse (more expensive)
        # Less tolerance for higher prices
        distance = price - max_range
        if distance <= range_size * 0.3:
            # Slightly over budget
            return 0.70 - (distance / (range_size * 0.3)) * 0.25
        elif distance <= range_size * 0.8:
            # Moderately over budget
            normalized_dist = (distance - range_size * 0.3) / (range_size * 0.5)
            return 0.45 - normalized_dist * 0.25
        elif distance <= range_size * 1.5:
            # Significantly over budget
            normalized_dist = (distance - range_size * 0.8) / (range_size * 0.7)
            return 0.20 - normalized_dist * 0.15
        else:
            # Way over budget
            return max(0.01, 0.05 * (1 - min(distance / (range_size * 3), 1)))
    
    def _parse_price_preference(self, preference):
        """Parse price preference string and return (min, max) tuple"""
        price_ranges = {
            "Under 200k": (0, 200000),
            "200k-300k": (200000, 300000),
            "300k-400k": (300000, 400000),
            "400k-500k": (400000, 500000),
            "500k-600k": (500000, 600000),
            "600k-700k": (600000, 700000),
            "700k-800k": (700000, 800000),
            "800k-1M": (800000, 1000000),
            "Over 1M": (1000000, 2000000),  # Assume max of 2M for open-ended
        }
        return price_ranges.get(preference)

    def get_score_breakdown(self, flat, preferences):
        """
        Get detailed score breakdown for debugging/display purposes.

        Returns:
            dict: Breakdown of scores for each criterion with explanations
        """
        breakdown = {}

        for criterion, weight in self.weights.items():
            pref_value = preferences.get(criterion, "")
            if pref_value:
                score = self._calculate_criterion_score(criterion, flat, pref_value)
                flat_value = flat.get(criterion, "N/A")
                
                breakdown[criterion] = {
                    "score": round(score * 100),
                    "weight": weight,
                    "weighted_score": round(score * weight * 100),
                    "preference": pref_value,
                    "actual": flat_value,
                    "match_quality": self._get_match_quality(score)
                }

        return breakdown
    
    def _get_match_quality(self, score):
        """Get qualitative description of match quality"""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.75:
            return "Very Good"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        elif score >= 0.2:
            return "Poor"
        else:
            return "Very Poor"


# Create global instance
score_calculator = ScoreCalculator()
