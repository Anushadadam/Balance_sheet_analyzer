# utils/plotting.py
import plotly.graph_objects as go
import pandas as pd

def create_bar_chart(df, x_col, y_col, title):
    """Creates an interactive bar chart using Plotly."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], name=title, text=df[y_col], texttemplate='%{y:,.2f}', textposition='outside'))
    fig.update_layout(
        title_text=title,
        xaxis_title=x_col.capitalize(),
        yaxis_title="Value (units as per report)",
        template="plotly_dark"
    )
    return fig

def create_line_chart(df, x_col, y_col, title):
    """Creates an interactive line chart for trends."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode='lines+markers', name=title))
    fig.update_layout(
        title_text=title,
        xaxis_title=x_col.capitalize(),
        yaxis_title="Value (units as per report)",
        template="plotly_dark"
    )
    return fig

def create_asset_liability_chart(df):
    """Creates a grouped bar chart comparing assets and liabilities over years."""
    fig = go.Figure()
    
    df['value'] = pd.to_numeric(df['value'])
    df['year'] = pd.to_numeric(df['year'])
    df = df.sort_values('year')

    assets_df = df[df['metric'] == 'Total Assets']
    liabilities_df = df[df['metric'] == 'Total Liabilities']

    if not assets_df.empty:
        fig.add_trace(go.Bar(x=assets_df['year'], y=assets_df['value'], name='Total Assets', marker_color='lightgreen'))
    if not liabilities_df.empty:
        fig.add_trace(go.Bar(x=liabilities_df['year'], y=liabilities_df['value'], name='Total Liabilities', marker_color='indianred'))

    fig.update_layout(
        barmode='group',
        title_text="Total Assets vs. Total Liabilities Over Years",
        xaxis_title="Year",
        yaxis_title="Value",
        template="plotly_dark",
        xaxis=dict(type='category')
    )
    return fig

# --- NEW FUNCTION FOR GROWTH PLOTTING ---
def create_growth_chart(df, metric_name, title):
    """
    Calculates and plots the year-over-year growth of a specific metric.
    """
    # 1. Filter the DataFrame for the specific metric
    metric_df = df[df['metric'] == metric_name].copy()
    
    # 2. Ensure data is numeric and sorted by year
    metric_df['value'] = pd.to_numeric(metric_df['value'])
    metric_df = metric_df.sort_values('year')

    # 3. Calculate Year-over-Year (YoY) percentage growth
    # pct_change() is a powerful pandas function for this
    metric_df['growth_pct'] = metric_df['value'].pct_change() * 100
    
    # The first year will have NaN growth, so we drop it for a cleaner plot
    metric_df.dropna(subset=['growth_pct'], inplace=True)
    
    if metric_df.empty:
        # Return None if there's not enough data to calculate growth (e.g., only one year)
        return None

    # 4. Create the bar chart for growth
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=metric_df['year'],
        y=metric_df['growth_pct'],
        name='YoY Growth',
        # Add text labels on the bars for clarity
        text=metric_df['growth_pct'].apply(lambda x: f'{x:+.2f}%'),
        textposition='auto'
    ))
    
    fig.update_layout(
        title_text=title,
        xaxis_title="Year",
        yaxis_title="Year-over-Year Growth (%)",
        template="plotly_dark",
        xaxis=dict(type='category'),
        yaxis=dict(ticksuffix="%")
    )
    
    return fig# utils/plotting.py
import plotly.graph_objects as go
import pandas as pd

def create_bar_chart(df, x_col, y_col, title):
    """Creates an interactive bar chart using Plotly."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], name=title, text=df[y_col], texttemplate='%{y:,.2f}', textposition='outside'))
    fig.update_layout(
        title_text=title,
        xaxis_title=x_col.capitalize(),
        yaxis_title="Value (units as per report)",
        template="plotly_dark"
    )
    return fig

def create_line_chart(df, x_col, y_col, title):
    """Creates an interactive line chart for trends."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode='lines+markers', name=title))
    fig.update_layout(
        title_text=title,
        xaxis_title=x_col.capitalize(),
        yaxis_title="Value (units as per report)",
        template="plotly_dark"
    )
    return fig

def create_asset_liability_chart(df):
    """Creates a grouped bar chart comparing assets and liabilities over years."""
    fig = go.Figure()
    
    df['value'] = pd.to_numeric(df['value'])
    df['year'] = pd.to_numeric(df['year'])
    df = df.sort_values('year')

    assets_df = df[df['metric'] == 'Total Assets']
    liabilities_df = df[df['metric'] == 'Total Liabilities']

    if not assets_df.empty:
        fig.add_trace(go.Bar(x=assets_df['year'], y=assets_df['value'], name='Total Assets', marker_color='lightgreen'))
    if not liabilities_df.empty:
        fig.add_trace(go.Bar(x=liabilities_df['year'], y=liabilities_df['value'], name='Total Liabilities', marker_color='indianred'))

    fig.update_layout(
        barmode='group',
        title_text="Total Assets vs. Total Liabilities Over Years",
        xaxis_title="Year",
        yaxis_title="Value",
        template="plotly_dark",
        xaxis=dict(type='category')
    )
    return fig

# --- NEW FUNCTION FOR GROWTH PLOTTING ---
def create_growth_chart(df, metric_name, title):
    """
    Calculates and plots the year-over-year growth of a specific metric.
    """
    # 1. Filter the DataFrame for the specific metric
    metric_df = df[df['metric'] == metric_name].copy()
    
    # 2. Ensure data is numeric and sorted by year
    metric_df['value'] = pd.to_numeric(metric_df['value'])
    metric_df = metric_df.sort_values('year')

    # 3. Calculate Year-over-Year (YoY) percentage growth
    # pct_change() is a powerful pandas function for this
    metric_df['growth_pct'] = metric_df['value'].pct_change() * 100
    
    # The first year will have NaN growth, so we drop it for a cleaner plot
    metric_df.dropna(subset=['growth_pct'], inplace=True)
    
    if metric_df.empty:
        # Return None if there's not enough data to calculate growth (e.g., only one year)
        return None

    # 4. Create the bar chart for growth
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=metric_df['year'],
        y=metric_df['growth_pct'],
        name='YoY Growth',
        # Add text labels on the bars for clarity
        text=metric_df['growth_pct'].apply(lambda x: f'{x:+.2f}%'),
        textposition='auto'
    ))
    
    fig.update_layout(
        title_text=title,
        xaxis_title="Year",
        yaxis_title="Year-over-Year Growth (%)",
        template="plotly_dark",
        xaxis=dict(type='category'),
        yaxis=dict(ticksuffix="%")
    )
    
    return fig
