class UserPreferences:
    """Class to store user preferences for flat search"""
    def __init__(self):
        self.flat_type = ""
        self.storey_range = ""
        self.floor_area_sqm = ""
        self.flat_model = ""
        self.price_range = ""
        self.favorite_flats = []  # List to store favorite flat IDs
    
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
    
    def add_to_favorites(self, flat_id):
        """Add a flat to favorites"""
        if flat_id not in self.favorite_flats:
            self.favorite_flats.append(flat_id)
            return True
        return False
    
    def remove_from_favorites(self, flat_id):
        """Remove a flat from favorites"""
        if flat_id in self.favorite_flats:
            self.favorite_flats.remove(flat_id)
            return True
        return False
    
    def is_favorite(self, flat_id):
        """Check if a flat is in favorites"""
        return flat_id in self.favorite_flats
    
    def get_favorites(self):
        """Get list of favorite flat IDs"""
        return self.favorite_flats.copy()
    
    def get_favorites_count(self):
        """Get count of favorite flats"""
        return len(self.favorite_flats)

# Create a global instance for the single user
user_preferences = UserPreferences()