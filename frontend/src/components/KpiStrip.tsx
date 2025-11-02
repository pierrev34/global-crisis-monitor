import React from 'react';
import { Summary } from '@/types/feed';

interface KpiStripProps {
  summary: Summary;
}

/**
 * KpiStrip - Three key metrics with week-over-week comparison
 */
export default function KpiStrip({ summary }: KpiStripProps) {
  const {
    total_incidents,
    countries_affected,
    human_rights_share,
    delta_pct,
  } = summary;

  const formatDelta = (delta: number | null | undefined) => {
    if (delta === null || delta === undefined) return null;
    const sign = delta > 0 ? '+' : '';
    return `${sign}${delta.toFixed(1)}%`;
  };

  const getDeltaColor = (delta: number | null | undefined) => {
    if (delta === null || delta === undefined) return 'text-text-muted';
    return delta > 0 ? 'text-green-600' : 'text-text-muted';
  };

  const kpis = [
    {
      label: 'Total Incidents',
      value: total_incidents.toLocaleString(),
      caption: 'past 7 days',
      delta: delta_pct,
      deltaText: delta_pct ? `vs previous 7 days: ${formatDelta(delta_pct)}` : null,
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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-5">
      {kpis.map((kpi, index) => (
        <div
          key={index}
          className="bg-white border border-border rounded-2xl p-5"
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
          {kpi.deltaText && (
            <div className={`text-xs font-medium mt-2 ${getDeltaColor(kpi.delta)}`}>
              {kpi.deltaText}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
