"""
Data models and cache management for the juvenile immigration API
"""
import pandas as pd

class DataCache:
    """Singleton class to manage data cache"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataCache, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._data = {
            'juvenile_cases': None,
            'proceedings': None,
            'reps_assigned': None, 
            'lookup_decisions': None,
            'lookup_juvenile': None,
            'analysis_filtered': None,
            'merged_data': None,
            'data_loaded': False
        }
        self._initialized = True
    
    def get(self, key):
        """Get data from cache"""
        return self._data.get(key)
    
    def set(self, key, value):
        """Set data in cache"""
        self._data[key] = value
    
    def get_all(self):
        """Get all cached data"""
        return self._data
    
    def clear(self):
        """Clear all cached data"""
        self._data = {
            'juvenile_cases': None,
            'proceedings': None,
            'reps_assigned': None, 
            'lookup_decisions': None,
            'lookup_juvenile': None,
            'analysis_filtered': None,
            'merged_data': None,
            'data_loaded': False
        }
    
    def is_loaded(self):
        """Check if data is loaded"""
        return self._data.get('data_loaded', False)
    
    def set_loaded(self, status=True):
        """Set data loaded status"""
        self._data['data_loaded'] = status
    
    def get_stats(self):
        """Get basic statistics about cached data"""
        stats = {}
        for key, data in self._data.items():
            if key != 'data_loaded' and data is not None:
                if isinstance(data, pd.DataFrame):
                    stats[key] = len(data)
                else:
                    stats[key] = "loaded"
        return stats

# Global cache instance
cache = DataCache()
