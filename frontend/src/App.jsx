import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import OverviewKPIs from './components/OverviewKPIs';
import AlertsTable from './components/AlertsTable';
import RiskDistributionChart from './components/RiskDistributionChart';
import RecentActivity from './components/RecentActivity';
import TimeMachineView from './components/TimeMachineView';
import { getAlerts, getTimeMachineSimulation } from './services/api';

const VIEW_CONFIG = {
  overview: { title: 'Overview', subtitle: 'Fleet-wide risk assessment summary' },
  alerts: { title: 'Active Alerts', subtitle: 'Vehicles predicted to face recall within 12 months' },
  timemachine: { title: 'Time Machine', subtitle: 'Historical recall prediction replay' },
};

export default function App() {
  const [activeView, setActiveView] = useState('overview');
  const [alerts, setAlerts] = useState([]);
  const [simData, setSimData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [alertsRes, simRes] = await Promise.all([
          getAlerts(),
          getTimeMachineSimulation('ford_explorer_2016_suspension'),
        ]);
        setAlerts(alertsRes);
        setSimData(simRes);
      } catch (err) {
        console.error('API load failed:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleInvestigate = (entityId) => {
    setActiveView('timemachine');
  };

  const { title, subtitle } = VIEW_CONFIG[activeView] || VIEW_CONFIG.overview;

  return (
    <div className="flex min-h-screen">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />

      <div className="flex-1 ml-[220px] flex flex-col">
        <TopBar title={title} subtitle={subtitle} />

        <main className="flex-1 p-5 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-[13px] text-zinc-500">Loading data...</div>
            </div>
          ) : activeView === 'overview' ? (
            <>
              <OverviewKPIs alerts={alerts} />
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2">
                  <AlertsTable alerts={alerts} onInvestigate={handleInvestigate} />
                </div>
                <div className="space-y-4">
                  <RiskDistributionChart alerts={alerts} />
                  <RecentActivity alerts={alerts} />
                </div>
              </div>
            </>
          ) : activeView === 'alerts' ? (
            <>
              <OverviewKPIs alerts={alerts} />
              <AlertsTable alerts={alerts} onInvestigate={handleInvestigate} />
            </>
          ) : activeView === 'timemachine' && simData ? (
            <TimeMachineView simulationData={simData} />
          ) : null}
        </main>
      </div>
    </div>
  );
}
