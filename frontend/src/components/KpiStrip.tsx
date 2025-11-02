import React from 'react';
import { Summary } from '@/types/feed';

interface KpiStripProps {
  summary: Summary;
}

/**
 * KpiStrip - Three key metrics for analyst dashboard
 * 
 * Shows essential metrics:
 * - Total incidents (7 days)
 * - Countries affected
 * - Human rights incidents percentage
 */
export default function KpiStrip({ summary }: KpiStripProps) {
  const {
    total_incidents,
    countries_affected,
    human_rights_share,
  } = summary;

  const kpis = [
    {
      label: 'Total Incidents',
      value: total_incidents.toLocaleString(),
      caption: 'past 7 days',
    },
    {
      label: 'Countries Affected',
      value: countries_affected.toLocaleString(),
      caption: 'past 7 days',
    },
    {
      label: 'Human-rights incidents',
      value: `${(human_rights_share * 100).toFixed(0)}%`,
      caption: 'of all incidents',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-7">
      {kpis.map((kpi, index) => (
        <div
          key={index}
          className="bg-white border border-border rounded-xl p-6"
        >
          <div className="text-xs font-medium text-text-muted uppercase tracking-wide-caps mb-3">
            {kpi.label}
          </div>
          <div className="text-5xl font-bold text-text-primary mb-2">
            {kpi.value}
          </div>
          <div className="text-sm text-text-muted">
            {kpi.caption}
          </div>
        </div>
      ))}
    </div>
  );
}
