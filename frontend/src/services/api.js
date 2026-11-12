import axios from 'axios';

const API_BASE = '/api';

export const getAlerts = async (category = null, make = null) => {
  const params = {};
  if (category) params.category = category;
  if (make) params.make = make;
  const res = await axios.get(`${API_BASE}/alerts`, { params });
  return res.data;
};

export const getTimeMachineSimulation = async (entityId = 'ford_explorer_2016_suspension') => {
  const res = await axios.get(`${API_BASE}/timemachine/${entityId}`);
  return res.data;
};

export const getVehicleDetail = async (entityId) => {
  const res = await axios.get(`${API_BASE}/vehicles/${entityId}`);
  return res.data;
};
