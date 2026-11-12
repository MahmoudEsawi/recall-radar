import axios from 'axios';

const API_BASE = '/api';

export const getAlerts = async (category = null, make = null) => {
  try {
    const params = {};
    if (category) params.category = category;
    if (make) params.make = make;
    const res = await axios.get(`${API_BASE}/alerts`, { params, timeout: 3000 });
    return res.data;
  } catch (err) {
    console.warn("Using local fallback alerts data:", err.message);
    return [
      {
        entity_id: "ford_explorer_2016_suspension",
        make: "FORD",
        model: "EXPLORER",
        year: 2016,
        component: "SUSPENSION",
        as_of_date: "2019-04",
        risk_score: 0.88,
        risk_category: "CRITICAL",
        predicted_recall_within_12m: true,
        lead_time_months: 8,
        complaint_count: 84,
        top_risk_factors: [
          { factor: "Complaint Velocity Surge", detail: "Complaints rose 210% over 60 days", impact: "Critical" },
          { factor: "Crash & Rollover Incidents", detail: "5 loss-of-control crash reports filed", impact: "Critical" },
          { factor: "NLP Keyword Cluster", detail: "Concentration of 'rear toe link fracture' phrases", impact: "High" }
        ],
        sample_complaints: [
          "While driving 65 mph on the highway, the rear suspension suddenly snapped. Vehicle fishtailed across two lanes.",
          "Rear toe link fractured without warning. Dealership confirmed part broke while exiting highway ramp.",
          "Heard loud clunking noise from rear right wheel, then loss of steering alignment and stability control warning."
        ],
        official_recall: {
          recalled: true,
          recall_date: "2019-12-10",
          campaign_id: "19V437000",
          defect_summary: "Rear toe link fracture leading to loss of steering control."
        }
      },
      {
        entity_id: "chevrolet_bolt_2020_electrical",
        make: "CHEVROLET",
        model: "BOLT EV",
        year: 2020,
        component: "ELECTRICAL SYSTEM",
        as_of_date: "2020-07",
        risk_score: 0.94,
        risk_category: "CRITICAL",
        predicted_recall_within_12m: true,
        lead_time_months: 4,
        complaint_count: 41,
        top_risk_factors: [
          { factor: "Thermal Runaway / Fire", detail: "7 reports of smoke or unattended combustion while charging", impact: "Critical" },
          { factor: "Poisson Regression Spike", detail: "Severe volume deviation (p-value < 0.001)", impact: "Critical" }
        ],
        sample_complaints: [
          "Vehicle was plugged into Level 2 charger in garage. Woke up to heavy smoke and flames from rear underside.",
          "Car caught fire while parked outside overnight with 100% battery charge. Complete loss of vehicle."
        ],
        official_recall: {
          recalled: true,
          recall_date: "2020-11-13",
          campaign_id: "20V701000",
          defect_summary: "High-voltage battery pack fire risk when charged to full capacity."
        }
      },
      {
        entity_id: "honda_civic_2017_airbags",
        make: "HONDA",
        model: "CIVIC",
        year: 2017,
        component: "AIR BAGS",
        as_of_date: "2019-06",
        risk_score: 0.79,
        risk_category: "HIGH",
        predicted_recall_within_12m: true,
        lead_time_months: 6,
        complaint_count: 62,
        top_risk_factors: [
          { factor: "Injury Severity Rate", detail: "3 reported hospital visits upon non-deployment in frontal collision", impact: "Critical" },
          { factor: "Volume Anomaly", detail: "Exceeded statistical complaint baseline by 3.8x", impact: "High" }
        ],
        sample_complaints: [
          "Involved in head-on collision at 35 mph. Seatbelts locked but steering wheel airbag failed to deploy.",
          "Front passenger airbag did not deploy during accident, resulting in passenger head injury."
        ],
        official_recall: {
          recalled: true,
          recall_date: "2019-12-20",
          campaign_id: "19V895000",
          defect_summary: "Front passenger airbag inflator malfunction during crash events."
        }
      },
      {
        entity_id: "toyota_rav4_2019_steering",
        make: "TOYOTA",
        model: "RAV4",
        year: 2019,
        component: "STEERING",
        as_of_date: "2021-02",
        risk_score: 0.42,
        risk_category: "MODERATE",
        predicted_recall_within_12m: false,
        lead_time_months: null,
        complaint_count: 18,
        top_risk_factors: [
          { factor: "Complaint Velocity", detail: "Flat growth over past 6 months", impact: "Low" }
        ],
        sample_complaints: [
          "Steering wheel makes slight clicking sound when making sharp turns at low speed."
        ],
        official_recall: null
      }
    ];
  }
};

const MULTI_TIMELINES = {
  ford_explorer_2016_suspension: {
    entity_id: "ford_explorer_2016_suspension",
    make: "FORD",
    model: "EXPLORER",
    year: 2016,
    component: "SUSPENSION",
    first_detected_date: "2019-04",
    official_recall_date: "2019-12-10",
    campaign_id: "19V437000",
    lead_time_months: 8,
    monthly_timeline: [
      { month: "2018-09", complaints: 2, risk_score: 0.12 },
      { month: "2018-10", complaints: 3, risk_score: 0.15 },
      { month: "2018-11", complaints: 4, risk_score: 0.18 },
      { month: "2018-12", complaints: 6, risk_score: 0.26 },
      { month: "2019-01", complaints: 9, risk_score: 0.38 },
      { month: "2019-02", complaints: 14, risk_score: 0.54 },
      { month: "2019-03", complaints: 22, risk_score: 0.72 },
      { month: "2019-04", complaints: 35, risk_score: 0.88 },
      { month: "2019-05", complaints: 42, risk_score: 0.91 },
      { month: "2019-06", complaints: 51, risk_score: 0.94 },
      { month: "2019-07", complaints: 58, risk_score: 0.95 },
      { month: "2019-08", complaints: 64, risk_score: 0.96 },
      { month: "2019-09", complaints: 71, risk_score: 0.97 },
      { month: "2019-10", complaints: 77, risk_score: 0.98 },
      { month: "2019-11", complaints: 80, risk_score: 0.98 },
      { month: "2019-12", complaints: 84, risk_score: 0.99 }
    ],
    top_risk_factors: [
      { factor: "Rear Toe Link Fractures", detail: "Sudden loss of steering control at highway speeds", impact: "Critical" },
      { factor: "Surge Slope", detail: "Exponential volume growth between Jan-Apr 2019", impact: "High" }
    ]
  },
  chevrolet_bolt_2020_electrical: {
    entity_id: "chevrolet_bolt_2020_electrical",
    make: "CHEVROLET",
    model: "BOLT EV",
    year: 2020,
    component: "ELECTRICAL SYSTEM",
    first_detected_date: "2020-07",
    official_recall_date: "2020-11-13",
    campaign_id: "20V701000",
    lead_time_months: 4,
    monthly_timeline: [
      { month: "2020-01", complaints: 1, risk_score: 0.08 },
      { month: "2020-02", complaints: 2, risk_score: 0.12 },
      { month: "2020-03", complaints: 3, risk_score: 0.19 },
      { month: "2020-04", complaints: 6, risk_score: 0.34 },
      { month: "2020-05", complaints: 11, risk_score: 0.58 },
      { month: "2020-06", complaints: 19, risk_score: 0.77 },
      { month: "2020-07", complaints: 28, risk_score: 0.94 },
      { month: "2020-08", complaints: 32, risk_score: 0.96 },
      { month: "2020-09", complaints: 36, risk_score: 0.97 },
      { month: "2020-10", complaints: 39, risk_score: 0.98 },
      { month: "2020-11", complaints: 41, risk_score: 0.99 }
    ],
    top_risk_factors: [
      { factor: "High Voltage Battery Smoke/Combustion", detail: "Cell defect causing internal short circuit", impact: "Critical" },
      { factor: "Poisson Surge Ratio", detail: "Incident rate 6.2x above EV baseline", impact: "Critical" }
    ]
  },
  honda_civic_2017_airbags: {
    entity_id: "honda_civic_2017_airbags",
    make: "HONDA",
    model: "CIVIC",
    year: 2017,
    component: "AIR BAGS",
    first_detected_date: "2019-06",
    official_recall_date: "2019-12-20",
    campaign_id: "19V895000",
    lead_time_months: 6,
    monthly_timeline: [
      { month: "2018-12", complaints: 3, risk_score: 0.15 },
      { month: "2019-01", complaints: 5, risk_score: 0.22 },
      { month: "2019-02", complaints: 8, risk_score: 0.31 },
      { month: "2019-03", complaints: 14, risk_score: 0.48 },
      { month: "2019-04", complaints: 21, risk_score: 0.62 },
      { month: "2019-05", complaints: 30, risk_score: 0.71 },
      { month: "2019-06", complaints: 39, risk_score: 0.79 },
      { month: "2019-07", complaints: 45, risk_score: 0.83 },
      { month: "2019-08", complaints: 50, risk_score: 0.87 },
      { month: "2019-09", complaints: 54, risk_score: 0.89 },
      { month: "2019-10", complaints: 58, risk_score: 0.92 },
      { month: "2019-11", complaints: 60, risk_score: 0.94 },
      { month: "2019-12", complaints: 62, risk_score: 0.96 }
    ],
    top_risk_factors: [
      { factor: "Airbag Deployment Failure", detail: "Non-deployment in moderate to severe front collisions", impact: "Critical" },
      { factor: "Hospital Injury Rate", detail: "Head and chest trauma reports", impact: "High" }
    ]
  }
};

export const getTimeMachineSimulation = async (entityId = 'ford_explorer_2016_suspension') => {
  try {
    const res = await axios.get(`${API_BASE}/timemachine/${entityId}`, { timeout: 3000 });
    return res.data;
  } catch (err) {
    console.warn("Using fallback timemachine data for:", entityId);
    return MULTI_TIMELINES[entityId] || MULTI_TIMELINES['ford_explorer_2016_suspension'];
  }
};
