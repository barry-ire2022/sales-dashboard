import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# -------------------------------
# Load data (CSV in same folder)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "sales_data.csv")

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError("sales_data.csv not found in app directory")

df = pd.read_csv(CSV_PATH)
df["Date"] = pd.to_datetime(df["Date"])

# -------------------------------
# Initialize Dash app
# -------------------------------
app = dash.Dash(__name__)
server = app.server  # Required for Render
app.title = "Interactive Sales Dashboard"

# -------------------------------
# Layout
# -------------------------------
app.layout = html.Div(
    style={"maxWidth": "1200px", "margin": "auto"},
    children=[
        html.H1("Interactive Sales Dashboard", style={"textAlign": "center"}),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
                "gap": "12px",
            },
            children=[
                dcc.Dropdown(
                    id="region-filter",
                    options=[{"label": r, "value": r} for r in sorted(df["Region"].unique())],
                    placeholder="Select Region",
                    multi=True,
                ),
                dcc.Dropdown(
                    id="category-filter",
                    options=[{"label": c, "value": c} for c in sorted(df["Category"].unique())],
                    placeholder="Select Category",
                    multi=True,
                ),
                dcc.Dropdown(
                    id="salesperson-filter",
                    options=[{"label": s, "value": s} for s in sorted(df["Salesperson"].unique())],
                    placeholder="Select Salesperson",
                    multi=True,
                ),
            ],
        ),

        html.Br(),

        html.Div(id="kpi-cards", style={"display": "flex", "gap": "20px"}),

        dcc.Graph(id="sales-trend"),
        dcc.Graph(id="sales-by-category"),
    ],
)

# -------------------------------
# Callbacks
# -------------------------------
@app.callback(
    Output("sales-trend", "figure"),
    Output("sales-by-category", "figure"),
    Output("kpi-cards", "children"),
    Input("region-filter", "value"),
    Input("category-filter", "value"),
    Input("salesperson-filter", "value"),
)
def update_dashboard(region, category, salesperson):
    filtered = df.copy()

    if region:
        filtered = filtered[filtered["Region"].isin(region)]
    if category:
        filtered = filtered[filtered["Category"].isin(category)]
    if salesperson:
        filtered = filtered[filtered["Salesperson"].isin(salesperson)]

    total_sales = filtered["Sales"].sum()
    avg_sales = filtered["Sales"].mean() if not filtered.empty else 0

    kpis = [
        html.Div(
            [
                html.H4("Total Sales"),
                html.H2(f"${total_sales:,.0f}"),
            ],
            style={"padding": "10px", "border": "1px solid #ccc"},
        ),
        html.Div(
            [
                html.H4("Average Sale"),
                html.H2(f"${avg_sales:,.0f}"),
            ],
            style={"padding": "10px", "border": "1px solid #ccc"},
        ),
    ]

    trend_fig = px.line(
        filtered, x="Date", y="Sales", title="Sales Over Time"
    )

    category_fig = px.bar(
        filtered,
        x="Category",
        y="Sales",
        color="Category",
        title="Sales by Category",
    )

    return trend_fig, category_fig, kpis


# -------------------------------
# Run app (local + cloud safe)
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
