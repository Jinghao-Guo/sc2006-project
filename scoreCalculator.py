"""
Score calculation module for HDB flats based on user preferences.
The score is calculated on a scale of 0-100, where 100 means perfect match.
"""


class ScoreCalculator:
    """Calculate compatibility scores between flats and user preferences"""

    def __init__(self):
        self.weights = {
            "flat_type": 0.25,
            "storey_range": 0.20,
            "floor_area_sqm": 0.20,
            "flat_model": 0.15,
            "price_range": 0.20,
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
        """Score flat type match (exact match = 1.0, no match = 0.0)"""
        if not flat_type or not preference:
            return 0
        return 1.0 if flat_type.upper() == preference.upper() else 0.0

    def _score_storey_range(self, storey_range, preference):
        """Score storey range match"""
        if not storey_range or not preference:
            return 0
        return 1.0 if storey_range.upper() == preference.upper() else 0.0

    def _score_floor_area(self, floor_area, preference):
        """Score floor area based on preference range"""
        if not floor_area or not preference:
            return 0

        try:
            floor_area = float(floor_area)
        except (ValueError, TypeError):
            return 0

        # Parse preference ranges
        if preference == "30-50":
            return (
                1.0
                if 30 <= floor_area <= 50
                else self._partial_area_score(floor_area, 30, 50)
            )
        elif preference == "51-70":
            return (
                1.0
                if 51 <= floor_area <= 70
                else self._partial_area_score(floor_area, 51, 70)
            )
        elif preference == "71-90":
            return (
                1.0
                if 71 <= floor_area <= 90
                else self._partial_area_score(floor_area, 71, 90)
            )
        elif preference == "91-110":
            return (
                1.0
                if 91 <= floor_area <= 110
                else self._partial_area_score(floor_area, 91, 110)
            )
        elif preference == "111-130":
            return (
                1.0
                if 111 <= floor_area <= 130
                else self._partial_area_score(floor_area, 111, 130)
            )
        elif preference == "131-150":
            return (
                1.0
                if 131 <= floor_area <= 150
                else self._partial_area_score(floor_area, 131, 150)
            )
        elif preference == "151+":
            return 1.0 if floor_area >= 151 else max(0, 1.0 - (151 - floor_area) / 20)

        return 0

    def _partial_area_score(self, area, min_range, max_range):
        """Calculate partial score for area outside preferred range"""
        range_size = max_range - min_range
        if area < min_range:
            distance = min_range - area
            return max(0, 1.0 - distance / range_size)
        elif area > max_range:
            distance = area - max_range
            return max(0, 1.0 - distance / range_size)
        return 1.0

    def _score_flat_model(self, flat_model, preference):
        """Score flat model match"""
        if not flat_model or not preference:
            return 0
        return 1.0 if flat_model.upper() == preference.upper() else 0.0

    def _score_price_range(self, price, preference):
        """Score price based on preference range"""
        if not price or not preference:
            return 0

        try:
            price = float(price)
        except (ValueError, TypeError):
            return 0

        # Parse preference ranges
        if preference == "Under 200k":
            return 1.0 if price < 200000 else max(0, 1.0 - (price - 200000) / 50000)
        elif preference == "200k-300k":
            return (
                1.0
                if 200000 <= price <= 300000
                else self._partial_price_score(price, 200000, 300000)
            )
        elif preference == "300k-400k":
            return (
                1.0
                if 300000 <= price <= 400000
                else self._partial_price_score(price, 300000, 400000)
            )
        elif preference == "400k-500k":
            return (
                1.0
                if 400000 <= price <= 500000
                else self._partial_price_score(price, 400000, 500000)
            )
        elif preference == "500k-600k":
            return (
                1.0
                if 500000 <= price <= 600000
                else self._partial_price_score(price, 500000, 600000)
            )
        elif preference == "600k-700k":
            return (
                1.0
                if 600000 <= price <= 700000
                else self._partial_price_score(price, 600000, 700000)
            )
        elif preference == "700k-800k":
            return (
                1.0
                if 700000 <= price <= 800000
                else self._partial_price_score(price, 700000, 800000)
            )
        elif preference == "800k-1M":
            return (
                1.0
                if 800000 <= price <= 1000000
                else self._partial_price_score(price, 800000, 1000000)
            )
        elif preference == "Over 1M":
            return 1.0 if price >= 1000000 else max(0, 1.0 - (1000000 - price) / 100000)

        return 0

    def _partial_price_score(self, price, min_range, max_range):
        """Calculate partial score for price outside preferred range"""
        range_size = max_range - min_range
        if price < min_range:
            distance = min_range - price
            return max(0, 1.0 - distance / range_size)
        elif price > max_range:
            distance = price - max_range
            return max(0, 1.0 - distance / range_size)
        return 1.0

    def get_score_breakdown(self, flat, preferences):
        """
        Get detailed score breakdown for debugging/display purposes.

        Returns:
            dict: Breakdown of scores for each criterion
        """
        breakdown = {}

        for criterion, weight in self.weights.items():
            pref_value = preferences.get(criterion, "")
            if pref_value:
                score = self._calculate_criterion_score(criterion, flat, pref_value)
                breakdown[criterion] = {
                    "score": round(score * 100),
                    "weight": weight,
                    "weighted_score": round(score * weight * 100),
                }

        return breakdown


# Create global instance
score_calculator = ScoreCalculator()
