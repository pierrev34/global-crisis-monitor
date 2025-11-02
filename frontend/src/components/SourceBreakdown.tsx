import React, { useState } from 'react';
import { SourceStat } from '@/types/feed';

interface SourceBreakdownProps {
  sources: SourceStat[];
  totalIncidents: number;
}

/**
 * SourceBreakdown - Simplified credibility widget
 */
export default function SourceBreakdown({ sources, totalIncidents }: SourceBreakdownProps) {
  const [showAllNgo, setShowAllNgo] = useState(false);
  const [showAllMedia, setShowAllMedia] = useState(false);

  if (!sources || sources.length === 0) {
    return (
      <div className="bg-white border border-border rounded-2xl p-5">
        <h3 className="text-base font-semibold text-text-primary mb-4">
          Source Transparency
        </h3>
        <div className="text-sm text-text-muted text-center py-12">
          No source data available
        </div>
      </div>
    );
  }

  // Separate NGO/UN sources from media
  const ngoSources = sources
    .filter((s) => s.type === 'ngo' || s.type === 'un')
    .sort((a, b) => b.count - a.count);
  const mediaSources = sources
    .filter((s) => s.type === 'media')
    .sort((a, b) => b.count - a.count);
  
  const ngoTotal = ngoSources.reduce((sum, s) => sum + s.count, 0);
  const mediaTotal = mediaSources.reduce((sum, s) => sum + s.count, 0);
  const ngoPercentage = (ngoTotal / totalIncidents) * 100;
  const mediaPercentage = (mediaTotal / totalIncidents) * 100;

  const displayedNgoSources = showAllNgo ? ngoSources : ngoSources.slice(0, 4);
  const displayedMediaSources = showAllMedia ? mediaSources : mediaSources.slice(0, 3);

  return (
    <div className="bg-white border border-border rounded-2xl p-5">
      <h3 className="text-base font-semibold text-text-primary mb-2">
        Source Transparency
      </h3>
      <p className="text-xs text-text-muted mb-4">
        Most incidents are sourced from institutional NGO / UN monitoring.
      </p>

      {/* Headline KPI */}
      <div className="mb-4">
        <div className="text-sm text-text-primary mb-3">
          <span className="font-semibold">{ngoTotal} / {totalIncidents}</span> from high-trust sources{' '}
          <span className="text-text-muted">({ngoPercentage.toFixed(0)}%)</span>
        </div>
        {/* Thinner progress bar with more spacing */}
        <div className="w-full bg-neutral-light h-1 rounded-full overflow-hidden">
          <div 
            className="h-full bg-primary rounded-full transition-all"
            style={{ width: `${ngoPercentage}%` }}
          />
        </div>
      </div>

      {/* 2-column breakdown - reduced padding */}
      <div className="flex gap-2 mb-5">
        <div className="flex-1 bg-blue-50 rounded-lg px-2.5 py-1.5">
          <div className="text-xs text-text-muted mb-0.5">NGO / UN</div>
          <div className="text-sm font-semibold text-primary">{ngoPercentage.toFixed(0)}%</div>
        </div>
        <div className="flex-1 bg-gray-50 rounded-lg px-2.5 py-1.5">
          <div className="text-xs text-text-muted mb-0.5">Media</div>
          <div className="text-sm font-semibold text-text-body">{mediaPercentage.toFixed(0)}%</div>
        </div>
      </div>

      {/* High-trust list */}
      {ngoSources.length > 0 && (
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wide-caps mb-2">
            High-trust (NGO / UN)
          </h4>
          <div className="space-y-0.5">
            {displayedNgoSources.map((source) => (
              <div key={source.name} className="flex justify-between items-center py-1">
                <span className="text-sm text-text-primary">{source.name}</span>
                <span className="text-sm text-text-muted">{source.count} <span className="text-xs">incidents</span></span>
              </div>
            ))}
          </div>
          {ngoSources.length > 4 && (
            <button
              onClick={() => setShowAllNgo(!showAllNgo)}
              className="text-xs text-primary hover:underline mt-2"
            >
              {showAllNgo ? 'Show less...' : 'Show more...'}
            </button>
          )}
        </div>
      )}

      {/* Media list */}
      {mediaSources.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wide-caps mb-2">
            Media reporting
          </h4>
          <div className="space-y-0.5">
            {displayedMediaSources.map((source) => (
              <div key={source.name} className="flex justify-between items-center py-1">
                <span className="text-sm text-text-primary">{source.name}</span>
                <span className="text-sm text-text-muted">{source.count} <span className="text-xs">incidents</span></span>
              </div>
            ))}
          </div>
          {mediaSources.length > 3 && (
            <button
              onClick={() => setShowAllMedia(!showAllMedia)}
              className="text-xs text-primary hover:underline mt-2"
            >
              {showAllMedia ? 'Show less...' : 'Show more...'}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
