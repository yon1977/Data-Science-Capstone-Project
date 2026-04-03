import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Launch site options
launch_sites = sorted(spacex_df['Launch Site'].unique())
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in launch_sites
]

# Create the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        all_sites_df = (
            spacex_df.groupby('Launch Site', as_index=False)['class']
            .sum()
            .rename(columns={'class': 'Successful Launches'})
        )
        fig = px.pie(
            all_sites_df,
            values='Successful Launches',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig

    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    outcome_df = (
        filtered_df['class']
        .value_counts()
        .rename_axis('Outcome')
        .reset_index(name='Count')
    )
    outcome_df['Outcome'] = outcome_df['Outcome'].map({1: 'Success', 0: 'Failure'})

    fig = px.pie(
        outcome_df,
        values='Count',
        names='Outcome',
        title=f'Success vs Failure for {entered_site}'
    )
    return fig


@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    title_site = 'All Sites' if entered_site == 'ALL' else entered_site

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=f'Payload vs. Launch Outcome for {title_site}'
    )
    return fig


if __name__ == '__main__':
    app.run(debug=True)
