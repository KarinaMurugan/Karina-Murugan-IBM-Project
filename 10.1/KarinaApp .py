# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[
                                                {'label': 'All Sites', 'value': 'ALL'}
                                            ] + [
                                                {'label': site, 'value': site}
                                                for site in spacex_df['Launch Site'].unique()
                                            ],
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                       2500: '2500',
                                                       5000: '5000',
                                                       7500: '7500',
                                                       10000: '10000'},
                                                value=[min_payload, max_payload]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-donut-chart` as output

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Show total success launches count for all sites
        fig = px.pie(spacex_df, 
                    values='class', 
                    names='Launch Site', 
                    title='Total Success Launches by Site',
                    hole=.3, # This creates the "Donut" hole
                    color_discrete_sequence=px.colors.qualitative.Pastel) # Changes the color palette
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Group data to get counts of 0 (Failure) and 1 (Success)
        filtered_df = filtered_df.groupby(['class']).size().reset_index(name='class count')
        
        fig = px.pie(filtered_df, 
                    values='class count', 
                    names='class', 
                    title=f'Success vs Failed Launches for {entered_site}',
                    hole=.3,
                    # Explicitly mapping Success (1) to Green and Failure (0) to Red
                    color='class',
                    color_discrete_map={1: '#28a745', 0: '#dc3545'}) 
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites',
            # Visual Improvements:
            hover_data=['Launch Site'], 
            template='plotly_dark', # Gives it a modern "dashboard" look
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {entered_site}',
            # Visual Improvements:
            template='plotly_dark',
            color_discrete_sequence=px.colors.qualitative.Vivid
        )

    # Global styling updates for both cases
    fig.update_traces(marker=dict(size=12, opacity=0.7, line=dict(width=1, color='White')))
    fig.update_layout(
        xaxis_title="Payload Mass (kg)",
        yaxis_title="Class (0=Failure, 1=Success)",
        font=dict(family="Arial", size=12)
    )
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
