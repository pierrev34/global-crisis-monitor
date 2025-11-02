import { TimeSeriesPoint, CountryIncident } from '@/types/feed';

/**
 * Analysis utilities for generating insights from dashboard data
 */

export interface Spike {
  date: string;
  total: number;
  rollingAvg: number;
  multiplier: number;
}

export interface CountryChange {
  country: string;
  current: number;
  previous: number;
  delta: number;
  deltaPct: number;
}

export interface CategoryChange {
  category: string;
  currentShare: number;
  previousShare: number;
  deltaPoints: number;
}

/**
 * Calculate 7-day rolling average for time series
 */
export function calculateRollingAverage(timeSeries: TimeSeriesPoint[], window: number = 7): number[] {
  const totals = timeSeries.map(point => 
    Object.values(point.categories).reduce((sum, val) => sum + val, 0)
  );
  
  const rollingAvgs: number[] = [];
  for (let i = 0; i < totals.length; i++) {
    const start = Math.max(0, i - window + 1);
    const windowData = totals.slice(start, i + 1);
    const avg = windowData.reduce((sum, val) => sum + val, 0) / windowData.length;
    rollingAvgs.push(avg);
  }
  
  return rollingAvgs;
}

/**
 * Detect spikes (days where total > 1.25x rolling average)
 */
export function detectSpikes(timeSeries: TimeSeriesPoint[], threshold: number = 1.25): Spike[] {
  const rollingAvgs = calculateRollingAverage(timeSeries, 7);
  const spikes: Spike[] = [];
  
  timeSeries.forEach((point, index) => {
    const total = Object.values(point.categories).reduce((sum, val) => sum + val, 0);
    const rollingAvg = rollingAvgs[index];
    
    if (total > rollingAvg * threshold) {
      spikes.push({
        date: point.date,
        total,
        rollingAvg,
        multiplier: total / rollingAvg,
      });
    }
  });
  
  return spikes;
}

/**
 * Find the day with largest increase
 */
export function findLargestDayIncrease(timeSeries: TimeSeriesPoint[]): {
  date: string;
  total: number;
  increase: number;
  topCategory: string;
} | null {
  if (timeSeries.length < 2) return null;
  
  let maxIncrease = 0;
  let maxDay = null;
  
  for (let i = 1; i < timeSeries.length; i++) {
    const prevTotal = Object.values(timeSeries[i - 1].categories).reduce((sum, val) => sum + val, 0);
    const currTotal = Object.values(timeSeries[i].categories).reduce((sum, val) => sum + val, 0);
    const increase = currTotal - prevTotal;
    
    if (increase > maxIncrease) {
      maxIncrease = increase;
      const topCategory = Object.entries(timeSeries[i].categories)
        .sort((a, b) => b[1] - a[1])[0][0];
      
      maxDay = {
        date: timeSeries[i].date,
        total: currTotal,
        increase,
        topCategory,
      };
    }
  }
  
  return maxDay;
}

/**
 * Compare category mix between two periods
 */
export function compareCategoryMix(
  current: TimeSeriesPoint[],
  previous: TimeSeriesPoint[]
): CategoryChange[] {
  const getCurrentShare = (category: string) => {
    const total = current.reduce((sum, point) => 
      sum + Object.values(point.categories).reduce((s, v) => s + v, 0), 0);
    const categoryTotal = current.reduce((sum, point) => 
      sum + (point.categories[category] || 0), 0);
    return (categoryTotal / total) * 100;
  };
  
  const getPreviousShare = (category: string) => {
    const total = previous.reduce((sum, point) => 
      sum + Object.values(point.categories).reduce((s, v) => s + v, 0), 0);
    const categoryTotal = previous.reduce((sum, point) => 
      sum + (point.categories[category] || 0), 0);
    return (categoryTotal / total) * 100;
  };
  
  const allCategories = new Set<string>();
  [...current, ...previous].forEach(point => {
    Object.keys(point.categories).forEach(cat => allCategories.add(cat));
  });
  
  const changes: CategoryChange[] = [];
  allCategories.forEach(category => {
    const currentShare = getCurrentShare(category);
    const previousShare = getPreviousShare(category);
    const deltaPoints = currentShare - previousShare;
    
    if (Math.abs(deltaPoints) > 1) { // Only include changes > 1 percentage point
      changes.push({
        category,
        currentShare,
        previousShare,
        deltaPoints,
      });
    }
  });
  
  return changes.sort((a, b) => Math.abs(b.deltaPoints) - Math.abs(a.deltaPoints));
}

/**
 * Format date for display
 */
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
