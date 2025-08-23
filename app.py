# Import packages
import dash
from dash import Dash, html, callback, Output, Input, State, dcc
import pandas as pd
import numpy as np
import pickle
import dash_bootstrap_components as dbc

# Initialize the app with a theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load data
vehicle_df = pd.read_csv('Cars.csv')

# Load models
model = pickle.load(open("Model/car-prediction.model", 'rb'))
scaler = pickle.load(open("Model/car-scalar.model", 'rb'))
label_car = pickle.load(open("Model/brand-label.model", 'rb'))
fuel_car = pickle.load(open("Model/brand-fuel.model", 'rb'))

# Categories
brand_cat = list(label_car.classes_)

fuel_cat = list(fuel_car.classes_)
# df[['year','max_power','engine','brand','mileage','fuel']]


num_cols = ['year', 'max_power', 'engine', 'mileage']

# Default values
default_values = {
    'year': 2017,
    'max_power': 82.4,
    'engine': 1197,
    'brand': 'Maruti',
    'mileage': 19.42,
    'fuel': 'Diesel',

}

# Layout
app.layout = dbc.Container([
    html.H1("🚗 Car Price Prediction", style={'textAlign': 'center'}),
    html.H2("Himalayan Chakky's AI Solution Pvt Ltd.", style={'textAlign': 'center'}),
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dbc.Label("Brand"),
            dcc.Dropdown(id="brand", options=brand_cat, value=brand_cat[0])
        ], width=4),

        dbc.Col([
            dbc.Label("Year"),
            dcc.Dropdown(
                id="year",
                options=[{"label": y, "value": y} for y in sorted(vehicle_df['year'].unique())],
                value=vehicle_df['year'].min()
            )
        ], width=4),

        dbc.Col([
            dbc.Label("Fuel"),
            dcc.Dropdown(id="fuel", options=fuel_cat, value=fuel_cat[0])
        ], width=4),
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Label("Mileage (km/l)"),
            dcc.Input(id="mileage", type="number", value=0, style={"width": "100%"})
        ], width=6),

        dbc.Col([
            dbc.Label("Max Power (bhp)"),
            dcc.Input(id="max_power", type="number", value=0, style={"width": "100%"})
        ], width=6),
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Label("Engine (cc)"),
            dcc.Input(id="engine", type="number", value=0, style={"width": "100%"})
        ], width=12),
    ]),

    html.Br(),
    dbc.Button("Predict Price", id="submit", color="primary", className="w-100"),

    html.Br(), html.Br(),
    html.Div(id="prediction_result", style={"textAlign": "center", "fontSize": "20px", "fontWeight": "bold"})
], fluid=True)

# df[['year','max_power','engine','brand','mileage','fuel']]
# Callback
@callback(
    Output("prediction_result", "children"),
    Input("submit", "n_clicks"),
    State("year", "value"),
    State("max_power", "value"),
    State("engine", "value"),
    State("brand", "value"),
    State("mileage", "value"),
    State("fuel", "value"), 
    prevent_initial_call=True
)


def predict_price(n, year, max_power, engine, brand, mileage, fuel):
    # Handle missing/invalid inputs
    features = {
        "year":year,
        "max_power": max_power,
        "engine": engine,
        "brand": brand,
        "mileage": mileage,
        "fuel": fuel
    }

    for f in features:
        if not features[f]:
            features[f] = default_values[f]
        elif f in num_cols and features[f] < 0:
            features[f] = default_values[f]

    # Convert to dataframe
    X = pd.DataFrame(features, index=[0])


    # Scale numeric
    X[num_cols] = scaler.transform(X[num_cols])

    # Encode categorical
    X['fuel'] = fuel_car.transform(X['fuel'])
    X['brand'] = label_car.transform(X['brand'])

    # Prediction
    price = np.round(np.exp(model.predict(X)), 2)[0]
    upper = price * 1.07
    lower = price * 0.93

    return f"💰 Predicted Price: ${price} | Range: {lower:.2f} – {upper:.2f}"


# Run app


    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
