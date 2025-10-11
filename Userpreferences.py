class UserPreferences:
    """Class to store user preferences for flat search"""
    def __init__(self):
        self.flat_type = ""
        self.storey_range = ""
        self.floor_area_sqm = ""
        self.flat_model = ""
        self.price_range = ""
    
    def set_preferences(self, flat_type="", storey_range="", floor_area_sqm="", flat_model="", price_range=""):
        """Set user preferences"""
        self.flat_type = flat_type
        self.storey_range = storey_range
        self.floor_area_sqm = floor_area_sqm
        self.flat_model = flat_model
        self.price_range = price_range
    
    def get_preferences(self):
        """Get user preferences as dictionary"""
        return {
            'flat_type': self.flat_type,
            'storey_range': self.storey_range,
            'floor_area_sqm': self.floor_area_sqm,
            'flat_model': self.flat_model,
            'price_range': self.price_range
        }
    
    def has_preferences(self):
        """Check if any preferences are set"""
        return bool(self.flat_type or self.storey_range or self.floor_area_sqm or self.flat_model or self.price_range)

# Create a global instance for the single user
user_preferences = UserPreferences()