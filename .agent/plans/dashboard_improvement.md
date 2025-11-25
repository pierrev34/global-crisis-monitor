# Implementation Plan - Global Rights Dashboard Improvements

## Problem
The current dashboard is a "simple" analytics tool. The user questions its utility and wants it to be more "impressive, interesting, and valuable". It currently lacks a native interactive map in the web app (it generates a separate HTML file), which is a missed opportunity for a "Global" monitor.

## Proposed Solution
1.  **Integrate Geospatial Visualization**: Move the map from a standalone HTML file to a first-class citizen in the Next.js dashboard.
2.  **Enhance Visual Storytelling**: Ensure the "Key Takeaways" and metrics tell a clear story (Insight-First).
3.  **Premium UI Polish**: Apply high-quality styling (fonts, spacing, colors) to match the "WSJ/Financial Times" aesthetic.

## Technical Implementation

### Phase 1: Verification & Assessment
- Run `npm run dev` to check the current state.
- Verify data loading from `public/data/human_rights_feed.json`.

### Phase 2: Map Integration
- Install `react-leaflet` or `mapbox-gl` (Leaflet is likely easier given the existing Folium/Python setup might export GeoJSON).
- Create a `CrisisMap` component in `frontend/src/components`.
- Feed it the `by_country` data from the JSON feed.
- Add it to `pages/index.tsx`, possibly replacing or augmenting the "Key Takeaways" section.

### Phase 3: UI/UX Refinement
- Review `tailwind.config.js` for color palette.
- Ensure typography is "editorial" (Serif headers, clean Sans-Serif body).
- Add "pulse" or "live" indicators for the latest incidents.

### Phase 4: "Value" Additions
- Add a "Focus Mode" or "Deep Dive" for specific high-incident regions.
- Ensure the "Source Breakdown" clearly highlights *credible* sources to build trust.

## Verification Plan
- Manual verification via Browser Subagent to ensure the map renders and interactions work.
- Check that the build passes (`npm run build`).
