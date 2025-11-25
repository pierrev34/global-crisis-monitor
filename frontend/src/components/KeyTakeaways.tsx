import React from 'react';
import { TimeSeriesPoint, CountryIncident, SourceStat } from '@/types/feed';
import { findLargestDayIncrease, compareCategoryMix, formatDate } from '@/utils/analysis';

interface KeyTakeawaysProps {
  timeSeries: TimeSeriesPoint[];
  countries: CountryIncident[];
  sources: SourceStat[];
  totalIncidents: number;
}

/**
 * KeyTakeaways - Auto-generated insights with trend indicators
 * 
 * Shows 3-4 key insights with visual indicators:
 * - Largest day-over-day increase
 * - Country with biggest 7d increase
 * - Category mix change
 * - Source coverage note
 */
export default function KeyTakeaways({
  timeSeries,
  countries,
  sources,
  totalIncidents,
}: KeyTakeawaysProps) {
  const insights: Array<{ text: string; type: 'spike' | 'trend' | 'info' }> = [];

  // 1. Largest day increase
  const largestDay = findLargestDayIncrease(timeSeries);
  if (largestDay && largestDay.increase > 2) {
    const dateStr = formatDate(largestDay.date);
    insights.push({
      text: `${dateStr} saw the biggest jump in incidents (${largestDay.total} total, +${largestDay.increase}), driven by ${largestDay.topCategory}.`,
      type: 'spike',
    });
  }

  // 2. Top country by incidents
  if (countries.length > 0) {
    const topCountry = countries.sort((a, b) => b.incidents - a.incidents)[0];
    if (topCountry.incidents >= 5) {
      insights.push({
        text: `${topCountry.country} reported ${topCountry.incidents} incidents, the most in this period.`,
        type: 'trend',
      });
    }
  }

  // 3. Category mix changes
  if (timeSeries.length >= 14) {
    const current = timeSeries.slice(-7);
    const previous = timeSeries.slice(-14, -7);
    const changes = compareCategoryMix(current, previous);

    if (changes.length > 0) {
      const biggest = changes[0];
      const direction = biggest.deltaPoints > 0 ? 'rose' : 'fell';
      const absChange = Math.abs(biggest.deltaPoints);

      if (absChange >= 3) {
        insights.push({
          text: `${biggest.category} ${direction} to ${biggest.currentShare.toFixed(0)}% of all reporting (${biggest.deltaPoints > 0 ? '+' : ''}${biggest.deltaPoints.toFixed(0)} pts).`,
          type: 'trend',
        });
      }
    }
  }

  // 4. Source coverage
  const ngoCount = sources.filter(s => s.type === 'ngo' || s.type === 'un').reduce((sum, s) => sum + s.count, 0);
  const coveragePercent = ((ngoCount / totalIncidents) * 100).toFixed(0);

  if (ngoCount > 0) {
    insights.push({
      text: `${coveragePercent}% of incidents came from NGO / UN sources → coverage remains high-trust.`,
      type: 'info',
    });
  }

  // If no insights, show fallback
  if (insights.length === 0) {
    insights.push({
      text: 'Monitoring ongoing. Check back for pattern analysis as more data accumulates.',
      type: 'info',
    });
  }

  const getIconForType = (type: 'spike' | 'trend' | 'info') => {
    switch (type) {
      case 'spike':
        return (
          <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        );
      case 'trend':
        return (
          <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        );
      case 'info':
        return (
          <svg className="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  return (
    <div className="bg-white border border-border rounded-2xl p-5 shadow-sm">
      <h3 className="text-base font-semibold text-text-primary mb-1">
        Key takeaways
      </h3>
      <p className="text-xs text-text-muted mb-4">
        Based on changes in the last 7–30 days
      </p>

      <div className="space-y-3">
        {insights.map((insight, index) => (
          <div key={index} className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              {getIconForType(insight.type)}
            </div>
            <p className="text-sm text-text-body leading-relaxed">
              {insight.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
