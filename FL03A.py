
def FL03A():
    from FL02_Sydney_Flights_Dataframe import generate_df
    import dash
    import dash_table
    from dash.dependencies import Input, Output
    import dash_core_components as dcc
    import dash_html_components as html
    import plotly.graph_objs as go
    import pandas as pd
    from datetime import date


    # seting global variables
    global sydney_df

    # importing data from FL02_Sydney_Flights_Dataframe
    sydney_df=generate_df()

    # Create today object to extract today's date
    today = date.today()

    # Create dataframe with only today's search result
    sydney_df_today=sydney_df.copy()

    # Only include latest search date
    sydney_df_today=sydney_df_today[sydney_df_today['Search Date']==today.strftime("%Y-%m-%d")]


    # activate Dash Server
    app = dash.Dash(__name__)

    # Change Flask environment from Production to Development
    get_ipython().run_line_magic('env', 'FLASK_ENV=development')


    # Create list of flight paths for drop down menu
    def flight_paths_dict_list():
        dictlist = []
        unique_list = sydney_df['Flight Path'].unique()
        for flight_path in unique_list:
            dictlist.append({'value': flight_path, 'label': flight_path})
        return dictlist

    dict_flight_paths=flight_paths_dict_list()



    # Creating the web app layout
    app.layout = html.Div([
        html.Div([
            html.H1('Flights Price Monitoring Dashboard'),
            html.H2('Choose Flight Path'),
            dcc.Dropdown(
                id='flight-path-dropdown',
                options=dict_flight_paths,
                multi=True,
                value = ["Air Mauritius MRU-PER-SYD option 1"]
            ),
            dcc.Graph(
                id='flights-price-comparison'
            )
        ], style={'width': '55%', 'display': 'inline-block'}),
        html.Div([
            html.H2('Lowest Price Trend Graph'),
            dcc.Graph(id='min-price-trend-graph'),
            html.P('')
        ], style={'width': '100%',  'display': 'inline-block'}),
        html.Div(id='hidden-email-alert', style={'display':'none'})
    ])


    # Flight Price Comparison Graph by Departure Date - Barchart

    @app.callback(Output('flights-price-comparison', 'figure'), [Input('flight-path-dropdown', 'value')])
    def update_bargraph(selected_dropdown_value):

        sydney_df_today_graph=sydney_df.copy()

        # Only include latest search date
        sydney_df_today_graph=sydney_df_today_graph[sydney_df_today_graph['Search Date']==today.strftime("%Y-%m-%d")]

        # Filter data frame based on flight path
        sydney_df_today_graph = sydney_df_today_graph[(sydney_df_today_graph['Flight Path'].isin(selected_dropdown_value))]

        # Converting Search Date to a datetime object to enable sorting
        sydney_df_today_graph['Departure Date']=pd.to_datetime(sydney_df_today_graph['Departure Date'],format='%d-%m-%Y').dt.date

        # Sort search date in ascending order
        sydney_df_today_graph.sort_values(by='Departure Date',inplace=True)

        # Generate trace list and assign to data variable
        data=generate_trace_list(sydney_df_today_graph, selected_dropdown_value)

        #layout

        layout = go.Layout(barmode = "group", title="Flight Price Comparison",
                       xaxis= dict(title= 'Departure Date',ticklen= 5,zeroline= False),
                       yaxis= dict(title= 'AUD',ticklen= 5,zeroline= False))

        figure=go.Figure(data=data,layout=layout)

        return figure

    def generate_trace_list(sydney_df_today_graph, selected_dropdown_value):
        # Make a timeline
        trace_list = []
        for value in selected_dropdown_value:
            selected_value_df = sydney_df_today_graph[sydney_df_today_graph['Flight Path']==value]
            trace = go.Bar(
                x=selected_value_df['Departure Date'],
                y=selected_value_df['Current Price AUD'],
                name = value
            )
            trace_list.append(trace)
        return trace_list


    return app
