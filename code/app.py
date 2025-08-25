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


num_cols = [ 'max_power', 'mileage']

# Default values
default_values = {
    'year': 2017,
    'max_power': 82.4,
    'brand': 'Maruti',
    'mileage': 19.42,
    'fuel': 'Diesel',

}

# Layout
# Layout
app.layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H1("🚗 Awesome Car Price Prediction", className="text-center mb-4"),
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
                    ], className="mb-3"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Mileage (km/l)"),
                            dcc.Input(id="mileage", type="number", value=0, style={"width": "100%"})
                        ], width=6),

                        dbc.Col([
                            dbc.Label("Max Power (bhp)"),
                            dcc.Input(id="max_power", type="number", value=0, style={"width": "100%"})
                        ], width=6),
                    ], className="mb-3"),

                    dbc.Button("Predict Price", id="submit", color="primary", className="w-100 mb-3"),
                    html.Div(id="prediction_result", className="text-center fs-4 fw-bold")
                ]),
                className="shadow p-4"
            ),
            width=8,  # make card 8/12 of the page width
            className="mx-auto my-5"  # center horizontally and add vertical margin
        )
    ),
    fluid=True
)


# df[['year','max_power','brand','mileage','fuel']]
# Callback
@callback(
    Output("prediction_result", "children"),
    Input("submit", "n_clicks"),
    State("year", "value"),
    State("max_power", "value"),
    State("brand", "value"),
    State("mileage", "value"),
    State("fuel", "value"), 
    prevent_initial_call=True
)


def predict_price(n, year, max_power, brand, mileage, fuel):
    # Handle missing/invalid inputs
    features = {
        "year":year,
        "max_power": max_power,
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
   

    return f"💰 Predicted Price: ${price}"


# Run app


    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
