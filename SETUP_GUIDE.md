# Setup Guide - ARGUS Human Rights Intelligence Dashboard

## Quick Setup

### Step 1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

This will install all required packages including React, Next.js, TypeScript, Tailwind CSS, and Recharts.

### Step 2: Start the Dashboard

```bash
npm run dev
```

Open your browser to http://localhost:3000

The dashboard will load with sample data immediately. You can explore the interface without running the Python pipeline first.

### Step 3: Generate Real Data (Optional)

To use real crisis data instead of mock data:

```bash
# From the project root
cd ..
python main.py
```

This fetches real data from 15+ sources and generates `public/data/human_rights_feed.json`. The dashboard will automatically use this real data.

## Production Deployment

### Build Static Site

```bash
cd frontend
npm run build
```

The static site is generated in `frontend/out/` and can be deployed to any web host.

### Deploy Options

GitHub Pages:
```bash
# Copy contents of out/ to gh-pages branch
```

Netlify:
```bash
# Drag and drop the out/ folder to Netlify dashboard
```

Vercel:
```bash
npm install -g vercel
vercel --prod
```

## Daily Updates

### Automated Pipeline

Set up a cron job or GitHub Action to run daily:

```bash
0 0 * * * cd /path/to/project && python main.py
```

Or use the included GitHub Actions workflow in `.github/workflows/update-crisis-map.yml`.

## Troubleshooting

### TypeScript errors before npm install

Expected behavior. Run `npm install` in the frontend directory to resolve.

### Dashboard shows "No Data Available"

Either use the included mock data or run `python main.py` to generate real data.

### Python dependencies missing

```bash
pip install -r requirements.txt
```

### Rate limit errors from Nominatim

The geocoding service has rate limits. The system includes delays and caching to handle this.

## Next Steps

Read `DASHBOARD_README.md` for detailed architecture documentation.

Check `frontend/README.md` for frontend-specific details.

Customize the dashboard by editing components in `frontend/src/components/`.
