import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import RiskCard from './components/RiskCard';
import AlertsTable from './components/AlertsTable';
import TimeMachineView from './components/TimeMachineView';
import { getAlerts, getTimeMachineSimulation } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('alerts');
  const [alerts, setAlerts] = useState([]);
  const [simulationData, setSimulationData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [alertsData, simData] = await Promise.all([
          getAlerts(),
          getTimeMachineSimulation('ford_explorer_2016_suspension')
        ]);
        setAlerts(alertsData);
        setSimulationData(simData);
      } catch (err) {
        console.error("Failed to load data from API, using fallback", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSelectEntity = (entityId) => {
    setActiveTab('timemachine');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
        <RiskCard
          stats={{
            criticalCount: alerts.filter(a => a.risk_category === 'CRITICAL').length || 2
          }}
        />

        {loading ? (
          <div className="flex items-center justify-center p-12 text-slate-500 text-sm">
            Loading RecallRadar intelligence...
          </div>
        ) : activeTab === 'alerts' ? (
          <AlertsTable alerts={alerts} onSelectEntity={handleSelectEntity} />
        ) : (
          <TimeMachineView simulationData={simulationData} />
        )}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500">
        RecallRadar © 2026 • Samsung AI Capstone Project • Team APORIA
      </footer>
    </div>
  );
}
