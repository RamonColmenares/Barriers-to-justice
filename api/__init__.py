"""
Juvenile Immigration API Package
Refactored for better maintainability and modularity
"""

from .models import cache
from .config import *
from .data_loader import load_data
from .data_processor import process_analysis_data, get_data_statistics
from .chart_generator import *
from .api_routes import *

__version__ = "1.0.0"
__author__ = "ET6-CDSP-group-19"
