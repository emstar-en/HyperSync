"""Cloud Provider Usage Examples"""
from hypersync.providers import ProviderManager
from hypersync.providers.adapters import AdapterFactory

# Setup
manager = ProviderManager()

# Add OpenAI provider
cred = manager.create_credential(
    name="openai-key",
    provider_type="openai",
    value="sk-..."
)

provider = manager.create_provider(
    name="OpenAI Production",
    provider_type="openai",
    credential_id=cred.credential_id
)

# Register models
gpt4 = manager.register_external_model(
    provider_id=provider.provider_id,
    external_model_id="gpt-4",
    display_name="GPT-4",
    model_type="chat",
    capabilities=["text_generation", "chat"]
)

# Use adapter
provider_config = provider.__dict__
credential_value = manager.get_credential(cred.credential_id, decrypt=True).encrypted_value
adapter = AdapterFactory.create_adapter(provider_config, credential_value)

# Make API call
import asyncio

async def test():
    result = await adapter.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(result)

asyncio.run(test())
