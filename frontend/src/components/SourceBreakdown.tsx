import React from 'react';
import { SourceStat } from '@/types/feed';

interface SourceBreakdownProps {
  sources: SourceStat[];
  totalIncidents: number;
}

/**
 * SourceBreakdown - Source transparency with trust metrics
 */
export default function SourceBreakdown({ sources, totalIncidents }: SourceBreakdownProps) {
  if (!sources || sources.length === 0) {
    return (
      <div className="bg-white border border-border rounded-xl p-6">
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
  const ngoSources = sources.filter((s) => s.type === 'ngo' || s.type === 'un');
  const mediaSources = sources.filter((s) => s.type === 'media');
  
  const ngoTotal = ngoSources.reduce((sum, s) => sum + s.count, 0);
  const ngoPercentage = (ngoTotal / totalIncidents) * 100;

  const SourceList = ({ sourceList, label }: { sourceList: SourceStat[], label: string }) => (
    <div className="mb-5">
      <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wide-caps mb-3">
        {label}
      </h4>
      <div className="space-y-2">
        {sourceList.slice(0, 8).map((source) => (
          <div key={source.name} className="flex justify-between items-center">
            <span className="text-sm text-text-primary">{source.name}</span>
            <span className="text-sm font-semibold text-text-body">{source.count}</span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="bg-white border border-border rounded-2xl p-5">
      <h3 className="text-base font-semibold text-text-primary mb-2">
        Source Transparency
      </h3>
      <p className="text-xs text-text-muted mb-5">
        Human-rights readers care about provenance; NGO and UN sources are prioritized.
      </p>

      {/* High-trust metric with progress bar */}
      <div className="mb-6 p-4 bg-bg rounded-lg">
        <div className="text-xs font-medium text-text-muted uppercase tracking-wide-caps mb-2">
          High-trust sources
        </div>
        <div className="text-2xl font-bold text-text-primary mb-2">
          {ngoTotal} / {totalIncidents}
        </div>
        <div className="w-full bg-neutral-light h-1.5 rounded-full overflow-hidden">
          <div 
            className="h-full bg-primary rounded-full transition-all"
            style={{ width: `${ngoPercentage}%` }}
          />
        </div>
        <div className="text-xs text-text-muted mt-1">
          {ngoPercentage.toFixed(0)}% from NGO / UN sources
        </div>
      </div>

      {ngoSources.length > 0 && (
        <SourceList
          sourceList={ngoSources}
          label="High-Trust (NGO / UN)"
        />
      )}

      {mediaSources.length > 0 && (
        <SourceList
          sourceList={mediaSources}
          label="Media Reporting"
        />
      )}
    </div>
  );
}
