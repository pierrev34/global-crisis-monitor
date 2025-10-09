# AI Chat Setup with Groq API

## Why Groq?

- **Free tier**: 30 requests/minute (plenty for personal use)
- **Open source models**: Llama 3 (8B parameter model)
- **Super fast**: ~500 tokens/second
- **Works for anyone**: No local installation needed

## Setup (2 minutes)

**1. Get Free API Key**

Visit: https://console.groq.com/keys

- Sign up (free)
- Click "Create API Key"
- Copy the key (starts with `gsk_...`)

**2. Add to .env File**

Create/edit `.env` in project root:

```bash
GROQ_API_KEY=gsk_your_actual_key_here
```

**3. Regenerate Map**

```bash
python3 main.py
```

**4. Deploy**

When deploying (GitHub Pages, Vercel, etc.), add the API key as an environment variable in your hosting platform.

## Usage

**AI will answer:**
- "What's happening in Gaza?"
- "Tell me about humanitarian crises"
- "Which regions have conflicts?"
- "Summarize the current situation"

**Fallback (no API key):**
- "gaza" → finds location
- "humanitarian" → lists crises
- "how many total" → shows stats

## Free Tier Limits

- **30 requests/minute**
- **6,000 requests/day**
- More than enough for typical usage

If you hit limits, system falls back to keyword search automatically.

## Security

The API key is embedded in the HTML but that's fine because:
1. It's rate-limited per key
2. Free tier has no charges
3. Can regenerate key anytime at console.groq.com
4. Only works for this specific use case (crisis queries)

For production, you'd typically use a backend proxy, but for a portfolio project this works great.
