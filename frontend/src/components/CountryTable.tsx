import React, { useState } from 'react';
import { CountryIncident, CATEGORY_BADGE_COLORS } from '@/types/feed';

interface CountryTableProps {
  countries: CountryIncident[];
  onSelectCountry: (country: CountryIncident) => void;
}

/**
 * CountryTable - Professional sortable country list
 * 
 * Shows country badges, incident counts, category pills, and last update
 */
export default function CountryTable({
  countries,
  onSelectCountry,
}: CountryTableProps) {
  const [sortBy, setSortBy] = useState<'incidents' | 'country'>('incidents');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  if (!countries || countries.length === 0) {
    return (
      <div className="bg-white border border-border rounded-xl p-6">
        <h3 className="text-base font-semibold text-text-primary mb-4">
          Countries
        </h3>
        <div className="text-sm text-text-muted text-center py-12">
          No country data available
        </div>
      </div>
    );
  }

  // Sort countries
  const sortedCountries = [...countries].sort((a, b) => {
    let comparison = 0;
    if (sortBy === 'incidents') {
      comparison = a.incidents - b.incidents;
    } else {
      comparison = a.country.localeCompare(b.country);
    }
    return sortOrder === 'asc' ? comparison : -comparison;
  });

  const toggleSort = (field: 'incidents' | 'country') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const getRelativeTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays === 0) {
      if (diffHours === 0) return 'Just now';
      return `${diffHours}h ago`;
    }
    if (diffDays === 1) return 'Yesterday';
    return `${diffDays}d ago`;
  };

  const getCategoryPillStyle = (category: string) => {
    const colors = CATEGORY_BADGE_COLORS[category] || { 
      bg: 'rgba(156, 163, 175, 0.12)', 
      text: '#4b5563' 
    };
    return {
      backgroundColor: colors.bg,
      color: colors.text,
    };
  };

  return (
    <div className="bg-white border border-border rounded-2xl overflow-hidden">
      <div className="p-5 border-b border-border">
        <h3 className="text-base font-semibold text-text-primary">
          Countries
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="border-b border-border bg-bg">
            <tr>
              <th
                className="text-left px-5 py-3 font-medium text-text-muted uppercase tracking-wide-caps text-xs cursor-pointer hover:bg-gray-100"
                onClick={() => toggleSort('country')}
              >
                Country {sortBy === 'country' && (
                  <span className="text-xs text-text-muted ml-1">
                    {sortOrder === 'desc' ? '↓' : '↑'}
                  </span>
                )}
              </th>
              <th
                className="text-right px-5 py-3 font-medium text-text-muted uppercase tracking-wide-caps text-xs cursor-pointer hover:bg-gray-100"
                onClick={() => toggleSort('incidents')}
              >
                Incidents {sortBy === 'incidents' && (
                  <span className="text-xs text-text-muted ml-1">
                    {sortOrder === 'desc' ? '↓' : '↑'}
                  </span>
                )}
              </th>
              <th className="text-left px-5 py-3 font-medium text-text-muted uppercase tracking-wide-caps text-xs">
                Dominant Category
              </th>
              <th className="text-right px-5 py-3 font-medium text-text-muted uppercase tracking-wide-caps text-xs">
                Last Update
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {sortedCountries.slice(0, 20).map((country) => (
              <tr
                key={country.country}
                className="hover:bg-bg cursor-pointer transition-colors h-12"
                onClick={() => onSelectCountry(country)}
              >
                <td className="px-5 py-3">
                  <div className="flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-md bg-neutral-light text-text-body text-xs font-semibold">
                      {country.iso2}
                    </span>
                    <span className="font-medium text-text-primary">
                      {country.country}
                    </span>
                  </div>
                </td>
                <td className="px-5 py-3 text-right">
                  <span className="font-semibold text-text-primary">
                    {country.incidents}
                  </span>
                </td>
                <td className="px-5 py-3">
                  <span 
                    className="inline-block px-2.5 py-1 rounded-md text-xs font-medium"
                    style={getCategoryPillStyle(country.top_category)}
                  >
                    {country.top_category}
                  </span>
                </td>
                <td className="px-5 py-3 text-right text-xs text-text-muted">
                  {getRelativeTime(country.latest)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sortedCountries.length > 20 && (
        <div className="px-5 py-3 border-t border-border text-center text-sm text-text-muted">
          Showing top 20 of {sortedCountries.length} countries
        </div>
      )}
    </div>
  );
}
