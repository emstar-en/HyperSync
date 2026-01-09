# Cloud Model Provider System

Connect to external cloud model providers (OpenAI, Anthropic, Azure, etc.)

## Quick Start

### Add a Provider

```bash
# OpenAI
hypersync provider add \
 --name "openai-prod" \
 --type openai \
 --api-key "sk-..."

# Anthropic
hypersync provider add \
 --name "anthropic-prod" \
 --type anthropic \
 --api-key "sk-ant-..."

# Azure OpenAI
hypersync provider add \
 --name "azure-prod" \
 --type azure \
 --api-key "..." \
 --base-url "https://your-resource.openai.azure.com"
```

### Use in Model Stacks

```bash
# Register external model
hypersync provider models provider-abc123

# Use in stack
hypersync stack create \
 --name "hybrid-stack" \
 --model reasoning:ext-model-gpt4 \
 --model local:llama-3-8b \
 --mode sequential
```

## Supported Providers

- **OpenAI**: GPT-4, GPT-3.5, embeddings
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
- **Azure OpenAI**: All OpenAI models via Azure
- **Google**: Gemini (coming soon)
- **Cohere**: Command, Embed (coming soon)

## Security

- Credentials encrypted at rest (AES-256-GCM)
- API keys never logged or exposed
- Automatic credential rotation support
- Audit logging for all API calls
