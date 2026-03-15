import plotly.graph_objects as go
from taipy.gui import notify


def create_forecast_chart(data):
    # Example: format your API data into a Pandas DataFrame
    # In a real app, 'data' would be the JSON from your API
    time =["00:00", "03:00", "06:00", "09:00", "12:00", "15:00"],
    temp = [18, 17, 19, 22, 25, 24]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time, 
        y=temp, 
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#3b82f6', width=4)
    ))
    
    fig.update_layout(
        template="plotly_dark",
        title="24-Hour Temperature Forecast",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# State
city = "Bengaluru"
forecast_fig = go.Figure() # Initial empty figure

def get_forecast(state):
    # 1. Fetch data (Logic)
    # 2. Update the Plotly Figure
    state.forecast_fig = create_forecast_chart(None) 
    notify(state, "info", "Chart updated!")

dashboard_md = """
# 🌤️ Weather Analytics

<|{city}|input|label=City|> <|Update|button|on_action=get_forecast|>

---

### Temperature Trend
<|chart|figure={forecast_fig}|engine=plotly|>
"""