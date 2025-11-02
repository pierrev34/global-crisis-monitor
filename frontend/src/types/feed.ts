/**
 * Type definitions for Human Rights Intelligence Dashboard
 * 
 * These types match the JSON contract from the Python exporter
 */

export interface IncidentItem {
  title: string;
  url: string;
  source: string;
  category: string;
  published: string;
}

export interface CountryIncident {
  country: string;
  iso2: string;
  lat: number;
  lon: number;
  incidents: number;
  top_category: string;
  latest: string;
  items: IncidentItem[];
}

export interface CategoryCount {
  name: string;
  count: number;
}

export interface SourceStat {
  name: string;
  count: number;
  type: 'ngo' | 'un' | 'media';
}

export interface TimeSeriesPoint {
  date: string;
  categories: Record<string, number>;
}

export interface Summary {
  total_incidents: number;
  countries_affected: number;
  human_rights_share: number;
  top_categories: CategoryCount[];
  source_mix: {
    ngo: number;
    media: number;
  };
}

export interface HumanRightsFeed {
  generated_at: string;
  window_days: number;
  summary: Summary;
  time_series: TimeSeriesPoint[];
  by_country: CountryIncident[];
  sources: SourceStat[];
}

/**
 * Category colors for professional analyst dashboard
 * Cool severity ramp: darkest navy to ice blue
 * All colors visible and readable on white background
 * Order matches stack from bottom (most severe) to top
 */
export const CATEGORY_COLORS: Record<string, string> = {
  'Human Rights Violations': '#0f172a',  // Very dark navy/ink - most serious
  'Political Conflicts': '#1d4ed8',      // Strong saturated blue
  'Humanitarian Crises': '#0ea5e9',      // Cool cyan - humanitarian
  'Health Emergencies': '#94a3b8',       // Blue-slate - low drama
  'Natural Disasters': '#bfdbfe',        // Light blue - more visible than ice
  'Economic Crises': '#64748b',
  'Environmental Issues': '#94a3b8',
};

/**
 * Category badge colors with light backgrounds
 */
export const CATEGORY_BADGE_COLORS: Record<string, { bg: string; text: string }> = {
  'Human Rights Violations': { bg: 'rgba(15, 23, 42, 0.08)', text: '#0f172a' },
  'Political Conflicts': { bg: 'rgba(29, 78, 216, 0.08)', text: '#1d4ed8' },
  'Humanitarian Crises': { bg: 'rgba(14, 165, 233, 0.1)', text: '#0369a1' },
  'Health Emergencies': { bg: 'rgba(148, 163, 184, 0.12)', text: '#475569' },
  'Natural Disasters': { bg: 'rgba(191, 219, 254, 0.3)', text: '#1e40af' },
  'Economic Crises': { bg: 'rgba(100, 116, 139, 0.12)', text: '#334155' },
  'Environmental Issues': { bg: 'rgba(148, 163, 184, 0.12)', text: '#475569' },
};

/**
 * Get color for a category, with fallback
 */
export function getCategoryColor(category: string): string {
  return CATEGORY_COLORS[category] || '#94a3b8';
}
