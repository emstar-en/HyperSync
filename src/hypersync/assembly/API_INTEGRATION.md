# API Integration

# Add to hypersync API setup

from hypersync.assembly.assembly_api import register_api as register_assembly_api

# In FastAPI app setup:
register_assembly_api(app)
