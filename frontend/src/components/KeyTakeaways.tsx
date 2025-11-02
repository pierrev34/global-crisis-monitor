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
 * KeyTakeaways - Auto-generated insights from the data
 * 
 * Shows 3-4 key insights:
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
  const insights: string[] = [];

  // 1. Largest day increase
  const largestDay = findLargestDayIncrease(timeSeries);
  if (largestDay && largestDay.increase > 2) {
    const dateStr = formatDate(largestDay.date);
    insights.push(
      `${dateStr} saw the biggest jump in incidents (${largestDay.total} total, +${largestDay.increase}), driven by ${largestDay.topCategory}.`
    );
  }

  // 2. Top country by incidents
  if (countries.length > 0) {
    const topCountry = countries.sort((a, b) => b.incidents - a.incidents)[0];
    if (topCountry.incidents >= 5) {
      insights.push(
        `${topCountry.country} reported ${topCountry.incidents} incidents, the most in this period.`
      );
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
        insights.push(
          `${biggest.category} ${direction} to ${biggest.currentShare.toFixed(0)}% of all reporting (${biggest.deltaPoints > 0 ? '+' : ''}${biggest.deltaPoints.toFixed(0)} pts).`
        );
      }
    }
  }

  // 4. Source coverage
  const ngoCount = sources.filter(s => s.type === 'ngo' || s.type === 'un').reduce((sum, s) => sum + s.count, 0);
  const coveragePercent = ((ngoCount / totalIncidents) * 100).toFixed(0);
  
  if (ngoCount > 0) {
    insights.push(
      `${coveragePercent}% of incidents came from NGO / UN sources → coverage remains high-trust.`
    );
  }

  // If no insights, show fallback
  if (insights.length === 0) {
    insights.push('Monitoring ongoing. Check back for pattern analysis as more data accumulates.');
  }

  return (
    <div className="bg-white border border-border rounded-2xl p-5">
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
              <div className="w-1.5 h-1.5 rounded-full bg-primary" />
            </div>
            <p className="text-sm text-text-body leading-relaxed">
              {insight}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
