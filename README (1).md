# 🏥 HHS Unaccompanied Alien Children (UAC) Care System Dashboard

An interactive, policy-aligned analytics dashboard for monitoring the U.S. Department of Health and Human Services (HHS) Unaccompanied Alien Children Program — built with **Streamlit** and **Plotly**.

---

## 📌 Project Overview

The UAC Program is a federally mandated initiative under which children apprehended by U.S. Customs and Border Protection (CBP) are transferred to HHS for medical screening, sheltering, and eventual placement with vetted sponsors.

This dashboard transforms raw daily operational counts into structured capacity insights — empowering decision-makers to assess system health, detect stress periods, and evaluate humanitarian response effectiveness.

---

## 📊 Dashboard Features

| Module | Description |
|---|---|
| **KPI Summary Cards** | Total system load, HHS/CBP population, peak load, net intake pressure, discharge ratio |
| **System Care Load** | HHS & CBP line chart with 7-day rolling average and peak annotation |
| **Net Intake Pressure** | Monthly red/green bar chart (positive = backlog building) |
| **Transfer vs Discharge Flow** | Grouped bar chart with daily/monthly toggle |
| **Discharge Offset Ratio** | Monthly bar chart — ratio ≥ 1× means system is relieving load |
| **Apprehensions Trend** | Daily/monthly apprehension volume into CBP custody |
| **CBP vs HHS Scatter** | Correlation plot color-coded by time progression |
| **Stress Timeline** | Color-coded capacity classification (Critical → Low) by month |
| **Cumulative Flows** | Running totals for transfers, discharges, and backlog |
| **Rolling Averages** | 14-day and 30-day smoothed HHS load with ±1σ volatility band |

---

## 📁 Project Structure

```
uac-dashboard/
│
├── app.py                                      ← Main Streamlit application
├── requirements.txt                            ← Python dependencies
├── HHS_Unaccompanied_Alien_Children_Program.csv ← Dataset (place here)
└── README.md                                   ← This file
```

---

## ⚙️ Setup & Installation

### 1. Clone / Download the project

```bash
# If using git
git clone <your-repo-url>
cd uac-dashboard
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Place the dataset

Ensure `HHS_Unaccompanied_Alien_Children_Program.csv` is in the **same folder** as `app.py`.

### 5. Run the dashboard

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

---

## 📋 Dataset Description

| Column | Description |
|---|---|
| `Date` | Reporting date |
| `Children apprehended and placed in CBP custody` | Daily CBP intake volume |
| `Children in CBP custody` | Active CBP care load |
| `Children transferred out of CBP custody` | Flow into HHS system |
| `Children in HHS Care` | Active HHS care load |
| `Children discharged from HHS Care` | Successful sponsor placements |

> **Date range:** January 2023 – December 2025 · **Rows:** ~1,170 reporting days

---

## 📈 Key Metrics Computed

| KPI | Formula |
|---|---|
| Total System Load | `CBP Custody + HHS Care` |
| Net Intake Pressure | `Transferred − Discharged` |
| Discharge Offset Ratio | `Discharged ÷ Transferred` |
| Care Load Volatility | 14-day rolling standard deviation |
| Backlog Accumulation | Cumulative net intake over time |

---

## 🎛️ Sidebar Controls

| Control | Options |
|---|---|
| **Filter by Year** | All Years / 2023 / 2024 / 2025 |
| **Granularity** | Monthly / Daily |
| **Chart Toggles** | CBP layer, 7-day rolling avg, Stress Timeline |

---

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — Web application framework
- **[Plotly](https://plotly.com/python/)** — Interactive charting
- **[Pandas](https://pandas.pydata.org/)** — Data manipulation
- **[NumPy](https://numpy.org/)** — Numerical operations

---

## 🏛️ Data Source

**U.S. Department of Health and Human Services (HHS)**  
Office of Refugee Resettlement (ORR)  
Unaccompanied Alien Children Program — Daily Operational Data

---

## 📝 Notes

- Data may contain gaps on weekends and federal holidays
- Rolling averages use `min_periods=1` to handle edge dates
- The discharge ratio is undefined (shown as 0) when transfers = 0

---

*Built as part of the Unified Mentor Data Analytics Project · HHS Humanitarian Response Evaluation*
