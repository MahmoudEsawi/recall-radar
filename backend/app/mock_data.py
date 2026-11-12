from typing import List, Dict

MOCK_ALERTS: List[Dict] = [
    {
        "entity_id": "ford_explorer_2016_suspension",
        "make": "FORD",
        "model": "EXPLORER",
        "year": 2016,
        "component": "SUSPENSION",
        "as_of_date": "2019-04",
        "risk_score": 0.88,
        "risk_category": "CRITICAL",
        "predicted_recall_within_12m": True,
        "lead_time_months": 8,
        "complaint_count": 84,
        "top_risk_factors": [
            {"factor": "Complaint Velocity Surge", "detail": "Complaints rose 210% over 60 days", "impact": "Critical"},
            {"factor": "Crash & Rollover Incidents", "detail": "5 loss-of-control crash reports filed", "impact": "Critical"},
            {"factor": "NLP Keyword Cluster", "detail": "Concentration of 'rear toe link fracture' phrases", "impact": "High"}
        ],
        "official_recall": {
            "recalled": True,
            "recall_date": "2019-12-10",
            "campaign_id": "19V437000",
            "defect_summary": "Rear toe link fracture leading to steering loss"
        }
    },
    {
        "entity_id": "honda_civic_2017_airbags",
        "make": "HONDA",
        "model": "CIVIC",
        "year": 2017,
        "component": "AIR BAGS",
        "as_of_date": "2019-06",
        "risk_score": 0.79,
        "risk_category": "HIGH",
        "predicted_recall_within_12m": True,
        "lead_time_months": 6,
        "complaint_count": 62,
        "top_risk_factors": [
            {"factor": "Injury Severity Rate", "detail": "3 reported hospital visits upon non-deployment", "impact": "Critical"},
            {"factor": "Poisson Regression Spike", "detail": "Volume exceeded statistical baseline by 3.8x", "impact": "High"},
            {"factor": "Defect Text Pattern", "detail": "K-Means cluster: 'airbag warning light illuminated'", "impact": "Moderate"}
        ],
        "official_recall": {
            "recalled": True,
            "recall_date": "2019-12-20",
            "campaign_id": "19V895000",
            "defect_summary": "Front passenger airbag inflator malfunction"
        }
    },
    {
        "entity_id": "chevrolet_bolt_2020_electrical",
        "make": "CHEVROLET",
        "model": "BOLT EV",
        "year": 2020,
        "component": "ELECTRICAL SYSTEM",
        "as_of_date": "2020-07",
        "risk_score": 0.94,
        "risk_category": "CRITICAL",
        "predicted_recall_within_12m": True,
        "lead_time_months": 4,
        "complaint_count": 41,
        "top_risk_factors": [
            {"factor": "Thermal Runaway / Fire", "detail": "7 reports of unattended smoke or combustion while charging", "impact": "Critical"},
            {"factor": "Linear Trend Slope", "detail": "High positive slope (p-value < 0.001)", "impact": "Critical"},
            {"factor": "Safety Classifier Output", "detail": "SVM safety score: 0.98 hazard probability", "impact": "High"}
        ],
        "official_recall": {
            "recalled": True,
            "recall_date": "2020-11-13",
            "campaign_id": "20V701000",
            "defect_summary": "High-voltage battery fire risk when charged to near full capacity"
        }
    },
    {
        "entity_id": "toyota_rav4_2019_steering",
        "make": "TOYOTA",
        "model": "RAV4",
        "year": 2019,
        "component": "STEERING",
        "as_of_date": "2021-02",
        "risk_score": 0.42,
        "risk_category": "MODERATE",
        "predicted_recall_within_12m": False,
        "lead_time_months": None,
        "complaint_count": 18,
        "top_risk_factors": [
            {"factor": "Complaint Velocity", "detail": "Flat growth over past 6 months", "impact": "Low"},
            {"factor": "Zero Fire/Crash", "detail": "Minor noise complaints with zero safety hazard reports", "impact": "Low"}
        ],
        "official_recall": None
    }
]

MOCK_TIME_MACHINE: Dict[str, Dict] = {
    "ford_explorer_2016_suspension": {
        "entity_id": "ford_explorer_2016_suspension",
        "make": "FORD",
        "model": "EXPLORER",
        "year": 2016,
        "component": "SUSPENSION",
        "first_detected_date": "2019-04",
        "official_recall_date": "2019-12-10",
        "lead_time_months": 8,
        "monthly_timeline": [
            {"month": "2018-09", "complaints": 2, "risk_score": 0.12},
            {"month": "2018-10", "complaints": 3, "risk_score": 0.15},
            {"month": "2018-11", "complaints": 4, "risk_score": 0.18},
            {"month": "2018-12", "complaints": 6, "risk_score": 0.26},
            {"month": "2019-01", "complaints": 9, "risk_score": 0.38},
            {"month": "2019-02", "complaints": 14, "risk_score": 0.54},
            {"month": "2019-03", "complaints": 22, "risk_score": 0.72},
            {"month": "2019-04", "complaints": 35, "risk_score": 0.88},  # Alert Triggered!
            {"month": "2019-05", "complaints": 42, "risk_score": 0.91},
            {"month": "2019-06", "complaints": 51, "risk_score": 0.94},
            {"month": "2019-07", "complaints": 58, "risk_score": 0.95},
            {"month": "2019-08", "complaints": 64, "risk_score": 0.96},
            {"month": "2019-09", "complaints": 71, "risk_score": 0.97},
            {"month": "2019-10", "complaints": 77, "risk_score": 0.98},
            {"month": "2019-11", "complaints": 80, "risk_score": 0.98},
            {"month": "2019-12", "complaints": 84, "risk_score": 0.99}   # Official Recall Announced!
        ],
        "top_risk_factors": [
            {"factor": "Rear Toe Link Fractures", "detail": "Sudden loss of steering control at highway speeds", "impact": "Critical"},
            {"factor": "Surge Slope", "detail": "Exponential volume growth between Jan-Apr 2019", "impact": "High"}
        ]
    }
}
