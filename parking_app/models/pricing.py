"""
Dynamic Parking Pricing Models
--------------------------------
1. Baseline Linear Pricing
2. Demand-Based Pricing
3. Competitive Pricing (with geospatial competitor awareness)
"""

import pandas as pd
import numpy as np

try:
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False


# ─── Competitor Data ──────────────────────────────────────────────────────────

COMPETITORS = [
    {"name": "CompA", "lat": 26.145, "lon": 91.737, "price": 50},
    {"name": "CompB", "lat": 26.144, "lon": 91.734, "price": 60},
    {"name": "CompC", "lat": 26.143, "lon": 91.735, "price": 70},
]


# ─── Entry Point ──────────────────────────────────────────────────────────────

def run_all_models(df: pd.DataFrame) -> dict:
    df = df.copy()

    # Parse datetime if columns exist
    if 'LastUpdatedDate' in df.columns and 'LastUpdatedTime' in df.columns:
        try:
            df['Datetime'] = pd.to_datetime(
                df['LastUpdatedDate'] + ' ' + df['LastUpdatedTime'],
                format="%d-%m-%Y %H:%M:%S"
            )
            df = df.sort_values('Datetime').reset_index(drop=True)
            labels = df['Datetime'].dt.strftime('%H:%M').tolist()
        except Exception:
            labels = [f'T{i}' for i in range(len(df))]
    else:
        labels = [f'T{i}' for i in range(len(df))]

    df = _baseline_linear_pricing(df)
    df = _demand_based_pricing(df)
    df = _competitive_pricing(df)

    n = len(df)
    occupancy_list = df['Occupancy'].astype(int).tolist() if 'Occupancy' in df.columns else [0] * n
    capacity_list  = df['Capacity'].astype(int).tolist()  if 'Capacity'  in df.columns else [100] * n

    return {
        'times':       list(range(n)),
        'labels':      labels,
        'baseline':    df['BaselinePrice'].round(2).tolist(),
        'demand':      df['FinalPrice'].round(2).tolist(),
        'competitive': df['CompetitivePrice'].round(2).tolist(),
        'occupancy':   occupancy_list,
        'capacity':    capacity_list,
        'comparison': [
            {
                'label':       str(labels[i]),
                'baseline':    round(float(df['BaselinePrice'].iloc[i]),    2),
                'demand':      round(float(df['FinalPrice'].iloc[i]),       2),
                'competitive': round(float(df['CompetitivePrice'].iloc[i]), 2),
                'occupancy':   int(df['Occupancy'].iloc[i]) if 'Occupancy' in df.columns else 0
            }
            for i in range(n)
        ]
    }


# ─── Model 1 : Baseline Linear ────────────────────────────────────────────────

def _baseline_linear_pricing(df: pd.DataFrame, alpha: float = 10,
                              initial_price: float = 50) -> pd.DataFrame:
    """
    Price increases linearly as occupancy ratio rises.
    new_price = prev_price + alpha * (occupancy / capacity)
    """
    prices = [initial_price]
    for i in range(1, len(df)):
        occ = df.iloc[i]['Occupancy']
        cap = df.iloc[i]['Capacity']
        occupancy_ratio = occ / max(cap, 1)
        prices.append(prices[-1] + alpha * occupancy_ratio)
    df['BaselinePrice'] = prices
    return df


# ─── Model 2 : Demand-Based ───────────────────────────────────────────────────

def _demand_based_pricing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Demand is a weighted combination of:
      occupancy rate, queue length, traffic, special day flag, vehicle type.
    Price is clipped to [0.5×base, 2×base].
    """
    TRAFFIC_MAP  = {'low': 1, 'medium': 2, 'high': 3}
    VEHICLE_MAP  = {'car': 1.0, 'bike': 0.8, 'bus': 1.2, 'truck': 1.5}
    BASE_PRICE   = 100
    LAMBDA       = 0.5

    df['TrafficLevel'] = (
        df['TrafficConditionNearby'].map(TRAFFIC_MAP).fillna(2)
        if 'TrafficConditionNearby' in df.columns else 2
    )
    df['VehicleTypeWeight'] = (
        df['VehicleType'].map(VEHICLE_MAP).fillna(1.0)
        if 'VehicleType' in df.columns else 1.0
    )
    df['OccupancyRate'] = df['Occupancy'] / df['Capacity'].replace(0, 1)

    queue   = df['QueueLength']  if 'QueueLength'  in df.columns else 0
    special = df['IsSpecialDay'] if 'IsSpecialDay' in df.columns else 0

    df['Demand'] = (
        1.2 * df['OccupancyRate']      +
        0.8 * queue                    -
        0.5 * df['TrafficLevel']       +
        1.0 * special                  +
        0.6 * df['VehicleTypeWeight']
    )

    dmin, dmax = df['Demand'].min(), df['Demand'].max()
    df['NormalizedDemand'] = (df['Demand'] - dmin) / max(dmax - dmin, 1e-10)
    df['DynamicPrice']     = BASE_PRICE * (1 + LAMBDA * df['NormalizedDemand'])
    df['FinalPrice']       = df['DynamicPrice'].clip(lower=BASE_PRICE * 0.5,
                                                     upper=BASE_PRICE * 2.0)
    return df


# ─── Model 3 : Competitive Pricing ────────────────────────────────────────────

def _competitive_pricing(df: pd.DataFrame, base_price: float = 50,
                         alpha: float = 10) -> pd.DataFrame:
    """
    Starts from baseline occupancy price, then adjusts based on
    competitor lots within 500 m.
    - If nearly full AND priced above avg competitor → reduce by ₹5 to attract
    - If competitor avg is higher than our price → raise by ₹3
    """
    def calc(row):
        occ_ratio  = row['Occupancy'] / max(row['Capacity'], 1)
        your_price = base_price + alpha * occ_ratio

        if GEOPY_AVAILABLE and 'Latitude' in row and 'Longitude' in row:
            your_loc     = (row['Latitude'], row['Longitude'])
            nearby_prices = [
                c['price'] for c in COMPETITORS
                if geodesic(your_loc, (c['lat'], c['lon'])).meters < 500
            ]
        else:
            nearby_prices = [c['price'] for c in COMPETITORS]

        avg_comp = np.mean(nearby_prices) if nearby_prices else your_price

        if occ_ratio > 0.9 and your_price > avg_comp:
            your_price -= 5
        elif avg_comp > your_price:
            your_price += 3

        return round(your_price, 2)

    df['CompetitivePrice'] = df.apply(calc, axis=1)
    return df
