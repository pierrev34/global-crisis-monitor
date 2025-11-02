import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Surface,
  Symbols,
} from 'recharts';
import { TimeSeriesPoint, getCategoryColor } from '@/types/feed';

interface IncidentsStackedChartProps {
  timeSeries: TimeSeriesPoint[];
}

/**
 * IncidentsStackedChart - Professional stacked bar chart
 * 
 * Shows daily incident counts with fixed category ordering
 */
export default function IncidentsStackedChart({
  timeSeries,
}: IncidentsStackedChartProps) {
  if (!timeSeries || timeSeries.length === 0) {
    return (
      <div className="bg-white border border-border rounded-xl p-6">
        <h3 className="text-base font-semibold text-text-primary mb-1">
          Incidents over time
        </h3>
        <p className="text-xs text-text-muted mb-4">
          Daily counts grouped by crisis category (UTC)
        </p>
        <div className="text-sm text-text-muted text-center py-12">
          No time series data available
        </div>
      </div>
    );
  }

  // Fixed category ordering - cool severity ramp
  // Darkest (most severe) at bottom to lightest at top
  const categories = [
    'Human Rights Violations',  // #0f172a - darkest navy, most serious
    'Political Conflicts',       // #1d4ed8 - strong blue
    'Humanitarian Crises',       // #0ea5e9 - cyan
    'Health Emergencies',        // #94a3b8 - slate
    'Natural Disasters',         // #dbeafe - ice blue
    'Economic Crises',
    'Environmental Issues',
  ].filter((cat) => {
    // Only include categories that exist in the data
    return timeSeries.some((point) => point.categories[cat]);
  });

  // Custom legend icon renderer with border for light colors
  const renderLegendIcon = (props: any) => {
    const { color } = props;
    // Add border to very light colors so they don't disappear on white
    const needsBorder = color === '#bfdbfe' || color === '#dbeafe';
    
    return (
      <svg width="10" height="10" style={{ marginRight: '4px', display: 'inline-block', verticalAlign: 'middle' }}>
        <rect
          x="0"
          y="0"
          width="10"
          height="10"
          fill={color}
          stroke={needsBorder ? '#cbd5e1' : 'none'}
          strokeWidth={needsBorder ? '1' : '0'}
        />
      </svg>
    );
  };

  // Custom tooltip with proper color indicators
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div
        style={{
          backgroundColor: 'white',
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          padding: '12px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: '8px', fontSize: '13px', color: '#0f172a' }}>
          {label}
        </div>
        {payload.map((entry: any, index: number) => {
          const isLightColor = entry.color === '#bfdbfe' || entry.color === '#dbeafe';
          
          return (
            <div
              key={`tooltip-${index}`}
              style={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: index < payload.length - 1 ? '6px' : '0',
              }}
            >
              <div
                style={{
                  width: '8px',
                  height: '8px',
                  backgroundColor: entry.color,
                  marginRight: '8px',
                  flexShrink: 0,
                  border: isLightColor ? '1px solid rgba(15, 23, 42, 0.06)' : 'none',
                }}
              />
              <span style={{ fontSize: '12px', color: '#0f172a', marginRight: '8px' }}>
                {entry.name}:
              </span>
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#0f172a' }}>
                {entry.value}
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  // Transform data for Recharts
  const chartData = timeSeries.map((point) => {
    const formattedDate = new Date(point.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
    
    const dataPoint: any = {
      date: formattedDate,
      fullDate: point.date,
    };
    
    categories.forEach((cat) => {
      dataPoint[cat] = point.categories[cat] || 0;
    });
    
    return dataPoint;
  });

  return (
    <div className="bg-white border border-border rounded-xl p-6">
      <h3 className="text-base font-semibold text-text-primary mb-1">
        Incidents over time
      </h3>
      <p className="text-xs text-text-muted mb-6">
        Daily counts grouped by crisis category (UTC)
      </p>

      <ResponsiveContainer width="100%" height={340}>
        <BarChart
          data={chartData}
          margin={{ top: 10, right: 10, left: -10, bottom: 5 }}
          barGap={0}
          barCategoryGap="12%"
        >
          <CartesianGrid 
            strokeDasharray="0" 
            stroke="#e2e8f0" 
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: '#0f172a' }}
            axisLine={{ stroke: '#e2e8f0' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#0f172a' }}
            axisLine={{ stroke: '#e2e8f0' }}
            tickLine={false}
            label={{ 
              value: 'Incidents', 
              angle: -90, 
              position: 'insideLeft', 
              style: { fontSize: 11, fill: '#0f172a' } 
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ 
              fontSize: '12px', 
              paddingTop: '16px',
            }}
            iconType="square"
            iconSize={10}
            align="left"
            formatter={(value, entry: any) => (
              <span>
                {renderLegendIcon({ color: entry.color })}
                <span style={{ color: '#0f172a' }}>{value}</span>
              </span>
            )}
            content={(props: any) => {
              const { payload } = props;
              return (
                <div style={{ fontSize: '12px', paddingTop: '16px', textAlign: 'left' }}>
                  {payload.map((entry: any, index: number) => (
                    <span key={`legend-${index}`} style={{ marginRight: '16px', display: 'inline-block' }}>
                      {renderLegendIcon({ color: entry.color })}
                      <span style={{ color: '#0f172a' }}>{entry.value}</span>
                    </span>
                  ))}
                </div>
              );
            }}
          />
          {categories.map((category, index) => (
            <Bar
              key={category}
              dataKey={category}
              stackId="a"
              fill={getCategoryColor(category)}
              radius={index === categories.length - 1 ? [6, 6, 0, 0] : [0, 0, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
