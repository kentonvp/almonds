import pandas as pd
import plotly
import plotly.graph_objects as go

import almonds.crud.category as crud_category
from almonds.schemas.transaction import Transaction


def category_pie_chart(transactions: list[Transaction]) -> str:
    df = pd.DataFrame(
        {
            "category_id": [txn.category_id for txn in transactions],
            "amount": [txn.amount for txn in transactions],
        }
    )

    category_df = df.groupby("category_id")["amount"].sum().reset_index()
    category_df = category_df[category_df["amount"] < 0]
    category_df["amount"] = category_df["amount"].abs()

    # TODO: Do better.
    category_df["category"] = category_df["category_id"].apply(
        lambda x: crud_category.get_category_by_id(x).name
    )

    total = category_df["amount"].sum()

    category_df["percent"] = category_df["amount"] / total * 100

    # Custom label: show label + percent only if > 1%
    category_df["label"] = category_df.apply(
        lambda row: (
            f"{row['category']}<br>{row['percent']:.1f}%" if row["percent"] > 1 else ""
        ),
        axis=1,
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=category_df["category"],
                values=category_df["amount"],
                text=category_df["label"],
                hole=0.4,  # Donut
                marker=dict(line=dict(color="#fff", width=2)),
                textinfo="text",
                hoverinfo="label+percent",
            )
        ]
    )

    fig.update_layout(title="Category Spending", showlegend=True)

    return plotly.io.to_html(fig, full_html=False)


def daily_spending_chart(transactions: list[Transaction]) -> str:
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
