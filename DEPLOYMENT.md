# 🌐 Deploying ARGUS Live to Your Website

## Quick Setup for pierrev.dev

### 1. Enable GitHub Pages
1. Go to your repository settings
2. Navigate to "Pages" in the sidebar
3. Set source to "Deploy from a branch"
4. Select "gh-pages" branch
5. Your live map will be available at: `https://pierrev34.github.io/global-crisis-monitor/`

### 2. Embed on pierrev.dev

Add this to your portfolio website:

```html
<!-- Full Page Embed -->
<iframe 
    src="https://pierrev34.github.io/global-crisis-monitor/" 
    width="100%" 
    height="800px" 
    style="border:none; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
</iframe>

<!-- Or just the map -->
<iframe 
    src="https://pierrev34.github.io/global-crisis-monitor/crisis_map.html" 
    width="100%" 
    height="600px" 
    style="border:none;">
</iframe>
```

### 3. Portfolio Section Example

```html
<section class="project">
    <h2>🌍 ARGUS - Global Crisis Monitor</h2>
    <p>
        AI-powered system that monitors global news in real-time, 
        classifies crises using machine learning, and creates 
        interactive world maps showing current global challenges.
    </p>
    
    <div class="project-demo">
        <iframe 
            src="https://pierrev34.github.io/global-crisis-monitor/" 
            width="100%" 
            height="700px"
            style="border:none; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.12);">
        </iframe>
    </div>
    
    <div class="project-tech">
        <span class="tech-badge">Python</span>
        <span class="tech-badge">AI/ML</span>
        <span class="tech-badge">NLP</span>
        <span class="tech-badge">Geospatial</span>
        <span class="tech-badge">Real-time Data</span>
    </div>
    
    <div class="project-links">
        <a href="https://github.com/pierrev34/global-crisis-monitor">View Code</a>
        <a href="https://pierrev34.github.io/global-crisis-monitor/">Live Demo</a>
    </div>
</section>
```

## 🤖 Automation Features

### Automatic Updates
- **Frequency**: Every 6 hours (4x daily)
- **Manual Trigger**: Available via GitHub Actions
- **Data Source**: GDELT Project + Demo fallback
- **Processing**: 50 articles per run with 0.4 confidence threshold

### What Gets Updated
- `crisis_map.html` - Interactive world map
- `crisis_summary.json` - Statistics and analytics
- `index.html` - Main dashboard page

### Monitoring
- Check GitHub Actions tab for run status
- View commit history for update timestamps
- Monitor via GitHub Pages deployment status

## 🎨 Customization Options

### Styling for Your Website
```css
.argus-embed {
    width: 100%;
    height: 80vh;
    border: none;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    transition: transform 0.3s ease;
}

.argus-embed:hover {
    transform: translateY(-5px);
}
```

### Responsive Design
```css
@media (max-width: 768px) {
    .argus-embed {
        height: 60vh;
        margin: 1rem 0;
    }
}
```

## 📊 Analytics Integration

### Track Engagement
```javascript
// Google Analytics event tracking
gtag('event', 'crisis_map_view', {
    'event_category': 'portfolio',
    'event_label': 'argus_demo'
});
```

## 🔧 Troubleshooting

### Common Issues
1. **Map not loading**: Check GitHub Pages deployment status
2. **Old data**: Verify GitHub Actions are running successfully
3. **Styling issues**: Ensure iframe dimensions are appropriate

### Manual Update
If needed, you can manually trigger updates:
1. Go to GitHub Actions tab
2. Select "Update Crisis Map" workflow
3. Click "Run workflow"

## 🚀 Going Live Checklist

- [ ] Repository is public
- [ ] GitHub Pages enabled on gh-pages branch
- [ ] GitHub Actions workflow is active
- [ ] First manual run completed successfully
- [ ] Embed code added to pierrev.dev
- [ ] Responsive design tested
- [ ] Analytics tracking configured (optional)

## 🌟 Portfolio Impact

This live demo showcases:
- **Real-time AI applications**
- **Full-stack development skills**
- **DevOps and automation**
- **Data visualization expertise**
- **Humanitarian technology focus**

Your visitors will see a constantly updating, AI-powered crisis monitoring system - demonstrating both technical sophistication and practical application of machine learning for social good.
