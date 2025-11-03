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
  Line,
  ComposedChart,
  ReferenceLine,
  Label,
  ReferenceArea,
} from 'recharts';
import { TimeSeriesPoint, getCategoryColor } from '@/types/feed';
import { calculateRollingAverage, detectSpikes, formatDate } from '@/utils/analysis';

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
      <div className="bg-white border border-border rounded-2xl p-5">
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
    'Natural Disasters',         // #bfdbfe - light blue
    'Economic Crises',
    'Environmental Issues',
  ].filter((cat) => {
    // Only include categories that exist in the data
    return timeSeries.some((point) => point.categories[cat]);
  });

  // Calculate rolling average and detect spikes
  const rollingAvgs = calculateRollingAverage(timeSeries, 7);
  const spikes = detectSpikes(timeSeries, 1.8); // Use conservative threshold
  const spikeSet = new Set(spikes.map(s => s.date));
  
  // Trim to show only days with data (remove long flat start)
  const firstDataIndex = timeSeries.findIndex(point => 
    Object.values(point.categories).reduce((sum, val) => sum + val, 0) > 0
  );
  const trimmedTimeSeries = firstDataIndex >= 0 ? timeSeries.slice(firstDataIndex) : timeSeries;

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

  // Transform data for Recharts (move before tooltip to avoid circular dependency)
  const chartData = trimmedTimeSeries.map((point, index) => {
    const originalIndex = firstDataIndex >= 0 ? firstDataIndex + index : index;
    const formattedDate = formatDate(point.date);
    
    const total = Object.values(point.categories).reduce((sum, val) => sum + val, 0);
    const isLast7Days = index >= trimmedTimeSeries.length - 7;
    const isSpike = spikeSet.has(point.date);
    
    const dataPoint: any = {
      date: formattedDate,
      fullDate: point.date,
      total,
      rollingAvg: rollingAvgs[originalIndex],
      isLast7Days,
      isSpike,
    };
    
    categories.forEach((cat) => {
      dataPoint[cat] = point.categories[cat] || 0;
    });
    
    return dataPoint;
  });

  // Custom tooltip with proper color indicators
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    // Calculate total for this day
    const total = payload.reduce((sum: number, entry: any) => sum + (entry.value || 0), 0);
    
    // Get rolling average for this day
    const dataPoint = chartData.find((d: any) => d.date === label);
    const rollingAvg = dataPoint?.rollingAvg;
    const vsAvg = rollingAvg && rollingAvg > 0 ? ((total - rollingAvg) / rollingAvg * 100) : null;

    // Filter out zero values and reverse order (darkest first)
    const nonZeroPayload = payload
      .filter((entry: any) => entry.value > 0)
      .reverse();

    return (
      <div className="bg-white border border-border rounded-xl p-3 shadow-lg">
        <div className="text-sm font-semibold text-text-primary mb-2">
          {label}
        </div>
        <div className="text-xs text-text-muted mb-2">
          Total: {total} incidents
        </div>
        {rollingAvg !== null && rollingAvg !== undefined && (
          <div className="text-xs text-text-muted mb-2">
            7-day avg: {rollingAvg.toFixed(1)}
            {vsAvg !== null && (
              <span className="ml-2">
                ({vsAvg > 0 ? '+' : ''}{vsAvg.toFixed(0)}%)
              </span>
            )}
          </div>
        )}
        <div className="space-y-1">
          {nonZeroPayload.map((entry: any, index: number) => {
            const color = entry.color;
            const needsBorder = color === '#bfdbfe' || color === '#dbeafe';
            
            return (
              <div key={`tooltip-${index}`} className="flex items-center gap-2">
                <div
                  className="w-2 h-2 rounded-sm flex-shrink-0"
                  style={{
                    backgroundColor: color,
                    border: needsBorder ? '1px solid rgba(15,23,42,0.2)' : 'none',
                  }}
                />
                <span className="text-xs" style={{ color: '#0f172a' }}>
                  {entry.name}: {entry.value}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white border border-border rounded-2xl p-5">
      <h3 className="text-base font-semibold text-text-primary mb-1">
        Incidents over time
      </h3>
      <p className="text-xs text-text-muted mb-5">
        Daily counts grouped by crisis category (UTC). Last 7 days emphasized.
      </p>

      <ResponsiveContainer width="100%" height={360}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 10, left: -10, bottom: 5 }}
          barGap={0}
          barCategoryGap="10%"
        >
          {/* Background highlight for last 7 days */}
          <defs>
            <pattern id="last7days" patternUnits="userSpaceOnUse" width="100%" height="100%">
              <rect width="100%" height="100%" fill="#f8fafc" opacity="0.5" />
            </pattern>
          </defs>
          
          <CartesianGrid 
            strokeDasharray="0" 
            stroke="#e2e8f0" 
            vertical={false}
          />
          
          {/* Highlight last 7 days */}
          {chartData.length >= 7 && (
            <ReferenceArea
              x1={chartData[chartData.length - 7].date}
              x2={chartData[chartData.length - 1].date}
              fill="#f0f9ff"
              fillOpacity={0.3}
              strokeOpacity={0}
            />
          )}
          
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
            domain={[0, (dataMax: number) => Math.ceil(dataMax * 1.15)]}
            label={{ 
              value: 'Incidents', 
              angle: -90, 
              position: 'insideLeft', 
              style: { fontSize: 11, fill: '#0f172a' } 
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="square"
            iconSize={10}
            wrapperStyle={{
              paddingTop: '20px',
              fontSize: '12px',
            }}
            content={(props: any) => {
              const { payload } = props;
              if (!payload) return null;

              // Separate line indicator from category bars
              const lineItem = payload.find((p: any) => p.value === '7-day average');
              const barItems = payload.filter((p: any) => p.value !== '7-day average');

              return (
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  flexWrap: 'wrap',
                  gap: '8px',
                  marginTop: '20px',
                }}>
                  {/* Show 7-day average first */}
                  {lineItem && (
                    <span key="legend-line" style={{ marginRight: '24px', display: 'inline-block' }}>
                      <span style={{ 
                        display: 'inline-block',
                        width: '14px',
                        height: '2px',
                        backgroundColor: '#94a3b8',
                        marginRight: '6px',
                        verticalAlign: 'middle',
                        borderTop: '2px dashed #94a3b8'
                      }} />
                      <span style={{ color: '#0f172a' }}>{lineItem.value}</span>
                    </span>
                  )}
                  {barItems.map((entry: any, index: number) => (
                    <span key={`legend-${index}`} style={{ marginRight: '16px', display: 'inline-block' }}>
                      {renderLegendIcon({ color: entry.color })}
                      <span style={{ color: '#0f172a' }}>{entry.value}</span>
                    </span>
                  ))}
                </div>
              );
            }}
          />
          {categories.map((category, index) => {
            const isLightCategory = category === 'Natural Disasters';
            return (
              <Bar
                key={category}
                dataKey={category}
                stackId="a"
                fill={getCategoryColor(category)}
                radius={index === categories.length - 1 ? [6, 6, 0, 0] : [0, 0, 0, 0]}
                stroke={isLightCategory ? '#e5e7eb' : 'none'}
                strokeWidth={isLightCategory ? 0.5 : 0}
              />
            );
          })}
          
          {/* Rolling average line */}
          <Line
            type="monotone"
            dataKey="rollingAvg"
            stroke="#94a3b8"
            strokeWidth={1.5}
            dot={false}
            name="7-day average"
            strokeDasharray="3 3"
          />
          
          {/* Spike indicators - slate dots matching cool theme */}
          {chartData.map((point: any, index: number) => {
            if (point.isSpike && index > 6) {
              return (
                <ReferenceLine
                  key={`spike-${index}`}
                  x={point.date}
                  stroke="none"
                >
                  <Label
                    value="●"
                    position="top"
                    style={{ fontSize: 10, fill: '#334155', fontWeight: 600 }}
                    offset={6}
                  />
                </ReferenceLine>
              );
            }
            return null;
          })}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
