import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import OverviewKPIs from './components/OverviewKPIs';
import AlertsTable from './components/AlertsTable';
import RiskDistributionChart from './components/RiskDistributionChart';
import RecentActivity from './components/RecentActivity';
import TimeMachineView from './components/TimeMachineView';
import InvestigationDrawer from './components/InvestigationDrawer';
import { getAlerts, getTimeMachineSimulation } from './services/api';

const VIEW_CONFIG = {
  overview: { title: 'Overview', subtitle: 'Fleet-wide early warning risk assessment' },
  alerts: { title: 'Active Alerts', subtitle: 'Vehicles predicted to face recall within 12 months' },
  timemachine: { title: 'Time Machine', subtitle: 'Historical recall prediction simulation' },
};

export default function App() {
  const [activeView, setActiveView] = useState('overview');
  const [alerts, setAlerts] = useState([]);
  const [simData, setSimData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Selected alert for slide-over drawer
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

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
    const alert = alerts.find(a => a.entity_id === entityId);
    if (alert) {
      setSelectedAlert(alert);
      setIsDrawerOpen(true);
    }
  };

  const handleLaunchTimeMachineFromDrawer = async (entityId) => {
    setIsDrawerOpen(false);
    setActiveView('timemachine');
    try {
      const data = await getTimeMachineSimulation(entityId);
      setSimData(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectCaseStudy = async (entityId) => {
    try {
      const data = await getTimeMachineSimulation(entityId);
      setSimData(data);
    } catch (e) {
      console.error(e);
    }
  };

  const { title, subtitle } = VIEW_CONFIG[activeView] || VIEW_CONFIG.overview;

  return (
    <div className="flex min-h-screen bg-zinc-950 text-zinc-100 font-sans">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />

      <div className="flex-1 ml-[220px] flex flex-col min-w-0">
        <TopBar title={title} subtitle={subtitle} />

        <main className="flex-1 p-6 space-y-5">
          {loading ? (
            <div className="flex items-center justify-center h-64 text-zinc-500 text-sm">
              Loading RecallRadar early warning systems...
            </div>
          ) : activeView === 'overview' ? (
            <>
              <OverviewKPIs alerts={alerts} />
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <div className="lg:col-span-2">
                  <AlertsTable alerts={alerts} onInvestigate={handleInvestigate} />
                </div>
                
                <div className="space-y-5">
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
            <TimeMachineView 
              simulationData={simData} 
              onSelectCaseStudy={handleSelectCaseStudy}
            />
          ) : null}
        </main>
      </div>

      {/* Investigation Slide-Over Drawer */}
      <InvestigationDrawer
        alert={selectedAlert}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        onOpenTimeMachine={handleLaunchTimeMachineFromDrawer}
      />
    </div>
  );
}
