"""
Storage Layer Complete Integration - Wires all storage backends.
"""
from hypersync.nvm.storage_integration import NVMStorageIntegration

class StorageLayerIntegration:
    """Complete storage layer wiring."""

    def __init__(self):
        self.nvm_storage = NVMStorageIntegration()
        self._backends = {}
        self._cache_layer = None

    def register_backend(self, name, backend):
        """Register storage backend."""
        self._backends[name] = backend
        self.nvm_storage.register_backend(name, backend)

    def store(self, key, value, backend="default", use_hvs=True):
        """Store with full integration."""
        if use_hvs:
            # Store with hyperbolic embedding
            result = self.nvm_storage.store_with_embedding(value)
        else:
            # Direct storage
            backend_obj = self._backends.get(backend)
            result = backend_obj.store(key, value)

        # Update cache
        if self._cache_layer:
            self._cache_layer.set(key, value)

        return result
