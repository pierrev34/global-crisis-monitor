import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import KpiStrip from '@/components/KpiStrip';
import IncidentsStackedChart from '@/components/IncidentsStackedChart';
import CountryTable from '@/components/CountryTable';
import CountryDetail from '@/components/CountryDetail';
import SourceBreakdown from '@/components/SourceBreakdown';
import { HumanRightsFeed, CountryIncident } from '@/types/feed';

/**
 * Main Dashboard Page - ARGUS Human Rights Intelligence
 * 
 * Insight-first, editorial presentation of global human rights incidents
 * Inspired by WSJ/FT data graphics: minimal, opinionated, crisp
 */
export default function Home() {
  const [feed, setFeed] = useState<HumanRightsFeed | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<CountryIncident | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // In production, this would fetch from the Python pipeline output
      // For now, try to load from public/data or fall back to mock data
      const response = await fetch('/data/human_rights_feed.json');
      
      if (!response.ok) {
        throw new Error('Failed to load feed data');
      }
      
      const data = await response.json();
      setFeed(data);
    } catch (err) {
      console.error('Error loading feed:', err);
      setError('Unable to load crisis data. Please run the Python pipeline first.');
      
      // Load mock data for development
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  const loadMockData = () => {
    // Mock data for development
    const mockFeed: HumanRightsFeed = {
      generated_at: new Date().toISOString(),
      window_days: 7,
      summary: {
        total_incidents: 108,
        countries_affected: 34,
        human_rights_share: 0.42,
        top_categories: [
          { name: 'Human Rights Violations', count: 45 },
          { name: 'Political Conflicts', count: 28 },
          { name: 'Humanitarian Crises', count: 19 },
        ],
        source_mix: {
          ngo: 61,
          media: 39,
        },
      },
      time_series: [
        { date: '2025-10-27', categories: { 'Human Rights Violations': 7, 'Political Conflicts': 4, 'Humanitarian Crises': 2 } },
        { date: '2025-10-28', categories: { 'Human Rights Violations': 5, 'Political Conflicts': 6, 'Humanitarian Crises': 3 } },
        { date: '2025-10-29', categories: { 'Human Rights Violations': 8, 'Political Conflicts': 5, 'Humanitarian Crises': 4 } },
        { date: '2025-10-30', categories: { 'Human Rights Violations': 6, 'Political Conflicts': 3, 'Humanitarian Crises': 2 } },
        { date: '2025-10-31', categories: { 'Human Rights Violations': 9, 'Political Conflicts': 4, 'Humanitarian Crises': 3 } },
        { date: '2025-11-01', categories: { 'Human Rights Violations': 5, 'Political Conflicts': 3, 'Humanitarian Crises': 2 } },
        { date: '2025-11-02', categories: { 'Human Rights Violations': 5, 'Political Conflicts': 3, 'Humanitarian Crises': 3 } },
      ],
      by_country: [
        {
          country: 'Ethiopia',
          iso2: 'ET',
          lat: 9.0,
          lon: 39.0,
          incidents: 9,
          top_category: 'Human Rights Violations',
          latest: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          items: [
            {
              title: 'Arbitrary detention of activists in Addis Ababa',
              url: 'https://www.hrw.org/news/2025/10/29/ethiopia-activists-detained',
              source: 'Human Rights Watch',
              category: 'Human Rights Violations',
              published: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            },
          ],
        },
        {
          country: 'Sudan',
          iso2: 'SD',
          lat: 12.86,
          lon: 30.22,
          incidents: 7,
          top_category: 'Humanitarian Crises',
          latest: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
          items: [
            {
              title: 'Millions displaced by ongoing conflict',
              url: 'https://www.unhcr.org/news/sudan-displacement-2025',
              source: 'UNHCR',
              category: 'Humanitarian Crises',
              published: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
            },
          ],
        },
      ],
      sources: [
        { name: 'Human Rights Watch', count: 22, type: 'ngo' },
        { name: 'Amnesty International', count: 17, type: 'ngo' },
        { name: 'UN OCHA', count: 14, type: 'un' },
        { name: 'BBC World', count: 9, type: 'media' },
      ],
    };
    
    setFeed(mockFeed);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-wsj-bg flex items-center justify-center">
        <div className="text-center">
          <div className="text-wsj-dark text-xl font-semibold mb-2">Loading...</div>
          <div className="text-wsj-gray text-sm">Fetching human rights intelligence</div>
        </div>
      </div>
    );
  }

  if (!feed) {
    return (
      <div className="min-h-screen bg-wsj-bg flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-wsj-dark text-xl font-semibold mb-2">No Data Available</div>
          <div className="text-wsj-gray text-sm">{error}</div>
        </div>
      </div>
    );
  }

  const generatedDate = new Date(feed.generated_at);

  return (
    <>
      <Head>
        <title>Human Rights Situation Dashboard</title>
        <meta name="description" content="Incidents from high-trust NGO and media sources" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-bg">
        {/* Header */}
        <header className="bg-white border-b border-border">
          <div className="max-w-[1200px] mx-auto px-6 py-5">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-2xl font-semibold text-text-primary mb-1">
                  Human Rights Situation Dashboard
                </h1>
                <p className="text-sm text-text-muted">
                  Incidents from high-trust NGO and media sources (last 7 days)
                </p>
              </div>
              <div className="text-right">
                <div className="text-xs text-text-muted uppercase tracking-wide-caps mb-0.5">
                  Updated
                </div>
                <div className="text-sm text-text-muted">
                  {generatedDate.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })} · {generatedDate.toLocaleTimeString('en-US', {
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true,
                  })}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="max-w-[1200px] mx-auto px-6 py-8">
          {/* KPI Strip */}
          <KpiStrip summary={feed.summary} />

          {/* Main Grid Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-7">
            {/* Left Column - Chart and Table */}
            <div className="lg:col-span-2 space-y-7">
              <IncidentsStackedChart timeSeries={feed.time_series} />
              <CountryTable
                countries={feed.by_country}
                onSelectCountry={setSelectedCountry}
              />
            </div>

            {/* Right Column - Source Breakdown */}
            <div className="lg:col-span-1">
              <SourceBreakdown 
                sources={feed.sources} 
                totalIncidents={feed.summary.total_incidents}
              />
            </div>
          </div>
        </div>

        {/* Country Detail Modal */}
        {selectedCountry && (
          <CountryDetail
            country={selectedCountry}
            onClose={() => setSelectedCountry(null)}
          />
        )}
      </main>
    </>
  );
}
