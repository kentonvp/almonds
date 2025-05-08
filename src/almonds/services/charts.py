import pandas as pd
import plotly
import plotly.graph_objects as go


def daily_spending_chart(transactions: list) -> str:
    df = pd.DataFrame(
        {
            "datetime": [txn.datetime for txn in transactions],
            "amount": [txn.amount for txn in transactions],
        }
    )

    df["date"] = pd.to_datetime(df["datetime"]).dt.date
    daily = df.groupby("date")["amount"].sum().reset_index()
    daily["total"] = daily["amount"].cumsum()

    pos = daily.copy()
    neg = daily.copy()
    pos["total"] = pos["total"].clip(lower=0)
    neg["total"] = neg["total"].clip(upper=0)

    # 3) Build the Plotly figure
    fig = go.Figure()

    # Positive (green) area up to zero
    fig.add_trace(
        go.Scatter(
            x=pos["date"],
            y=pos["total"],
            mode="none",
            fill="tozeroy",
            name="Positive",
            fillcolor="rgba(0, 200, 0, 0.5)",
        )
    )

    # Negative (red) area down to zero
    fig.add_trace(
        go.Scatter(
            x=neg["date"],
            y=neg["total"],
            mode="none",
            fill="tozeroy",
            name="Negative",
            fillcolor="rgba(200, 0, 0, 0.5)",
        )
    )

    fig.update_layout(
        title="Daily Spending",
        xaxis_title="Date",
        yaxis_title="Spending",
        template="plotly_white",
        showlegend=False,
    )

    # Convert figure to HTML for rendering
    return plotly.io.to_html(fig, full_html=False)
