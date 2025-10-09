# AI Chat Setup (Optional)

The chatbot works in two modes:

## Keyword Mode (Default)
- No setup required
- Basic search and filtering
- Works immediately

## AI Mode (Requires Ollama)
- Natural conversation
- Understands context
- Better query understanding

### Setup Ollama (5 minutes)

**1. Install Ollama**
```bash
# Mac/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from: https://ollama.com
```

**2. Download Model**
```bash
# Lightweight 3B model (2GB, fast)
ollama pull llama3.2:3b

# Start Ollama service
ollama serve
```

**3. Regenerate Map**
```bash
python3 main.py
```

The system auto-detects if Ollama is running. If available, you'll see "(AI mode)" in the chat welcome message.

### Try It

**AI Mode queries:**
- "What's happening in Gaza right now?"
- "Tell me about humanitarian crises"
- "Which regions have the most conflicts?"
- "Explain the situation in Ukraine"

**Keyword fallback:**
- "gaza" → finds location
- "humanitarian" → lists matching crises
- "how many total" → shows stats
- "list all" → top 10 locations

### Troubleshooting

**Chat says "keyword mode"?**
```bash
# Check if Ollama running
curl http://localhost:11434/api/tags

# Start it
ollama serve

# In another terminal
python3 main.py
```

**Slow responses?**
- llama3.2:3b should respond in 2-5 seconds
- Requires ~2GB RAM
- First query may be slower (model loading)

**Want to disable AI mode?**
- Stop Ollama: `killall ollama`
- Will fall back to keyword mode automatically
