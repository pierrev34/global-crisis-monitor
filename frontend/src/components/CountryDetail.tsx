import React from 'react';
import { CountryIncident, getCategoryColor, CATEGORY_BADGE_COLORS } from '@/types/feed';

interface CountryDetailProps {
  country: CountryIncident;
  onClose: () => void;
}

/**
 * CountryDetail - Professional modal for country-specific details
 */
export default function CountryDetail({ country, onClose }: CountryDetailProps) {
  // Calculate category breakdown
  const categoryBreakdown: Record<string, number> = {};
  country.items.forEach((item) => {
    categoryBreakdown[item.category] = (categoryBreakdown[item.category] || 0) + 1;
  });

  const categories = Object.entries(categoryBreakdown).sort((a, b) => b[1] - a[1]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-border p-5 flex justify-between items-start rounded-t-2xl">
          <div>
            <h2 className="text-xl font-semibold text-text-primary mb-1">
              {country.country}
            </h2>
            <p className="text-sm text-text-muted">
              {country.incidents} incidents (past 7 days)
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-text-muted hover:text-text-primary transition-colors p-1"
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Category Breakdown */}
        <div className="p-6 border-b border-border">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wide-caps mb-4">
            Category Breakdown
          </h3>
          <div className="space-y-3">
            {categories.map(([category, count]) => {
              const percentage = (count / country.incidents) * 100;
              return (
                <div key={category}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-text-primary">{category}</span>
                    <span className="text-sm text-text-muted">{count} ({percentage.toFixed(0)}%)</span>
                  </div>
                  <div className="w-full bg-neutral-light h-1.5 rounded-full overflow-hidden">
                    <div
                      className="h-full transition-all rounded-full"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: getCategoryColor(category),
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Items */}
        <div className="p-6">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wide-caps mb-4">
            Recent Incidents
          </h3>
          <div className="space-y-4">
            {country.items.map((item, index) => {
              const publishedDate = new Date(item.published);
              const isNGO = item.source.toLowerCase().includes('human rights watch') ||
                           item.source.toLowerCase().includes('amnesty') ||
                           item.source.toLowerCase().includes('unhcr') ||
                           item.source.toLowerCase().includes('un ');
              
              const categoryColors = CATEGORY_BADGE_COLORS[item.category] || { 
                bg: 'rgba(156, 163, 175, 0.12)', 
                text: '#4b5563' 
              };

              return (
                <div key={index} className="border-l-2 border-primary pl-4 py-2">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-text-primary hover:text-primary transition-colors mb-2 block"
                  >
                    {item.title}
                  </a>
                  <div className="flex flex-wrap gap-2 items-center text-xs mt-2">
                    <span 
                      className={`px-2 py-1 rounded-md font-medium ${isNGO ? 'bg-dark text-white' : 'bg-neutral-light text-text-body'}`}
                    >
                      {item.source}
                    </span>
                    <span 
                      className="px-2 py-1 rounded-md font-medium"
                      style={{
                        backgroundColor: categoryColors.bg,
                        color: categoryColors.text,
                      }}
                    >
                      {item.category}
                    </span>
                    <span className="text-text-muted">
                      {publishedDate.toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
