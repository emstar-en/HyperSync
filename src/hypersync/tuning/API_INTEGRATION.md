# API Integration

# Add to hypersync API setup

from hypersync.tuning.stable_api import register_api as register_tuning_api

# In FastAPI app setup:
register_tuning_api(app)
