# Agent Lightning Integration Plan for BabyAGI

## Overview

Agent Lightning is a Microsoft Research project that enables training AI agents with Reinforcement Learning (RL), Automatic Prompt Optimization, and Supervised Fine-tuning with minimal code changes. This document outlines how to integrate it with BabyAGI.

## Why Agent Lightning for BabyAGI?

### Benefits

| Feature | Benefit for BabyAGI |
|---------|---------------------|
| **Zero Code Change** | Minimal integration - just add `@agl.rollout` decorator and `agl.emit_reward()` |
| **Ollama Compatible** | Works with OpenAI-compatible APIs (Ollama has this!) |
| **Tool Selection Training** | Train agent to pick the right tool for each request |
| **Prompt Optimization** | Automatically improve system prompts |
| **Self-Improvement** | Learn from execution traces and rewards |

### Current BabyAGI Architecture

```
User Query → Telegram Bot → chat_with_functions() → LiteLLM → Ollama (llama3.2)
                                ↓
                         Tool Execution (NCA Toolkit, Crypto, etc.)
                                ↓
                           Response
```

### Proposed Architecture with Agent Lightning

```
User Query → Telegram Bot → @agl.rollout decorated function
                                ↓
                         chat_with_functions() → LLM Proxy → Ollama
                                ↓                         ↓
                         Tool Execution              Traces captured
                                ↓                         ↓
                         agl.emit_reward() ← User Feedback
                                ↓
                         LightningStore → Training Algorithm
                                ↓
                         Updated Prompts/Model
```

## Integration Steps

### Phase 1: Basic Tracing (No Training)

Add tracing to capture execution data without modifying behavior.

```python
# babyagi/functionz/packs/default/function_calling_chat.py

import agentlightning as agl

@func.register_function(
    metadata={"description": "..."},
    imports=["litellm", "json", "agentlightning"],
    dependencies=["get_function_wrapper", "execute_function_wrapper"]
)
@agl.rollout  # Add this decorator
def chat_with_functions(chat_history, available_function_names) -> str:
    # ... existing code ...
    
    # After getting response, emit reward based on success
    if tool_calls:
        # Successful tool usage
        agl.emit_reward(1.0, attributes={"tool_used": function_name})
    else:
        # Direct response
        agl.emit_reward(0.5, attributes={"direct_response": True})
    
    return assistant_response
```

### Phase 2: LLM Proxy Integration

Route Ollama calls through Agent Lightning's LLM Proxy to capture all LLM interactions.

```python
# Start LLM Proxy pointing to Ollama
import agentlightning as agl

# Ollama has OpenAI-compatible API at localhost:11434/v1
llm_proxy = agl.LLMProxy(
    port=43886,
    model_list=[{
        "model_name": "llama3.2",
        "litellm_params": {
            "model": "openai/llama3.2",
            "api_base": "http://localhost:11434/v1",
        },
    }],
    store=store_server,
)
```

Then update BabyAGI to use the proxy:
```python
# In .env or code
OLLAMA_BASE_URL = "http://localhost:43886/v1"  # Point to proxy instead of direct Ollama
```

### Phase 3: Reward Signals from Telegram

Capture user feedback as reward signals:

```python
# In telegram_bot.py

# Track message IDs for reward correlation
pending_rewards = {}

async def handle_message(update, context):
    # ... existing message handling ...
    
    # Store message for potential reward
    pending_rewards[message_id] = {
        "rollout_id": current_rollout_id,
        "timestamp": time.time()
    }

async def handle_reaction(update, context):
    """Handle emoji reactions as reward signals"""
    reaction = update.message_reaction.new_reaction[0].emoji
    
    # Map reactions to rewards
    reward_map = {
        "👍": 1.0,    # Positive
        "❤️": 1.0,    # Very positive
        "👎": -1.0,   # Negative
        "🎉": 1.0,    # Great response
    }
    
    reward = reward_map.get(reaction, 0.0)
    
    if message_id in pending_rewards:
        agl.emit_reward(reward, attributes={
            "source": "telegram_reaction",
            "reaction": reaction
        })
```

### Phase 4: Training (Optional - Requires GPU)

For actual model training, you'll need:

1. **GPU Resources**: At least one 40GB GPU for VERL training
2. **Dataset**: Collect traces from Phase 1-3
3. **Training Script**:

```python
# train_babyagi.py

import agentlightning as agl
from babyagi.functionz.packs.default.function_calling_chat import chat_with_functions

async def train_agent():
    trainer = agl.Trainer(
        agent=chat_with_functions,
        algorithm=agl.VERLAlgorithm(),  # or PPOAlgorithm
        store=agl.LightningStoreClient("http://localhost:45993"),
    )
    
    await trainer.train(
        dataset="collected_traces.parquet",
        epochs=10,
        learning_rate=1e-5,
    )
```

## Quick Start (Local Testing)

```bash
# 1. Install Agent Lightning
pip install agentlightning

# 2. Start the Lightning Store
agl store --port 45993

# 3. Run BabyAGI with tracing (Phase 1)
python telegram_bot.py

# 4. View traces
agl dashboard --port 45993
```

## Compatibility Notes

### Ollama + Agent Lightning

✅ **Compatible** - Ollama provides OpenAI-compatible API at `http://localhost:11434/v1`

Agent Lightning's LLM Proxy supports:
- OpenAI-compatible APIs ✅
- vLLM servers ✅
- Direct OpenAI ✅

### LiteLLM + Agent Lightning

✅ **Compatible** - Both use OpenAI-compatible interfaces

BabyAGI uses LiteLLM which can point to any OpenAI-compatible endpoint, including Agent Lightning's proxy.

## Requirements

### For Tracing Only (Phase 1-3)
- `pip install agentlightning`
- No GPU required
- Works with existing Ollama setup

### For Training (Phase 4)
- GPU with 40GB+ VRAM
- Ray cluster for distributed training
- VERL dependencies: `pip install agentlightning[verl]`

## Example: Minimal Integration

```python
# babyagi/traced_chat.py

import agentlightning as agl
from babyagi.functionz.packs.default.function_calling_chat import chat_with_functions as original_chat

# Initialize tracer
tracer = agl.OtelTracer()
store = agl.InMemoryLightningStore()

@agl.rollout
async def chat_with_tracing(chat_history, available_function_names) -> str:
    """Wrapped chat function with Agent Lightning tracing"""
    try:
        result = original_chat(chat_history, available_function_names)
        agl.emit_reward(1.0, attributes={"status": "success"})
        return result
    except Exception as e:
        agl.emit_reward(-1.0, attributes={"status": "error", "error": str(e)})
        raise

# Usage in telegram_bot.py
# response = await chat_with_tracing(chat_history, function_names)
```

## Next Steps

1. **Install Agent Lightning**: `pip install agentlightning`
2. **Add tracing decorators** to key functions
3. **Collect execution data** for a few days
4. **Analyze traces** to identify improvement opportunities
5. **Optionally train** if you have GPU resources

## Resources

- [Agent Lightning Documentation](https://microsoft.github.io/agent-lightning/)
- [Agent Lightning GitHub](https://github.com/microsoft/agent-lightning)
- [VERL Paper](https://arxiv.org/abs/2508.03680)
- [Ollama OpenAI Compatibility](https://github.com/ollama/ollama/blob/main/docs/openai.md)