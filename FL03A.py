
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
        dash_table.DataTable(
            id='datatable-interactivity',
            columns=[
                {"name": i, "id": i} for i in sydney_df_today.columns
            ],
            style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['Departure Date', 'Flight ID']
            ],
            style_data_conditional=[
                {
                    'if': {'row_index': 5},
                    'backgroundColor': 'rgb(204, 204, 255)'
                }
            ],
            style_header={
                'backgroundColor': 'rgb(51, 51, 255)',
                'fontWeight': 'bold',
                'color':'white'
            },
            data=sydney_df_today.to_dict('records'),
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable=False,
            row_selectable=False,
            row_deletable=False,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 10,
            hidden_columns=['Flight Path','Destination','Airline','Search Date'],
        ),
        html.Div(id='datatable-interactivity-container')
    ],style={'width': '40%', 'display': 'inline-block','marginLeft': 25}),
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

    # Flight Path Minimum Price Trend - Linechart

    @app.callback(Output('min-price-trend-graph', 'figure'), [Input('flight-path-dropdown', 'value')])
    def update_linegraph(selected_dropdown_value):

        # Create a copy of source data to filter
        sydney_df_trend=sydney_df.copy()

        sydney_df_trend = sydney_df_trend[(sydney_df_trend['Flight Path'].isin(selected_dropdown_value))]

        sydney_df_trend=pd.pivot_table(sydney_df_trend,index='Flight Path',columns='Search Date',values='Current Price AUD',aggfunc='min')

        sydney_df_trend=sydney_df_trend.stack().reset_index()
        sydney_df_trend.columns=['Flight Path','Search Date','Current Price AUD']

         # Generate trace list and assign to data variable
        data=generate_trace_list_linechart(sydney_df_trend, selected_dropdown_value)

        #layout

        layout = go.Layout(barmode = "group", title="Flight Path Minimum Price Trend",
                       xaxis= dict(title= 'Search Date',ticklen= 5,zeroline= False),
                       yaxis= dict(title= 'AUD',ticklen= 5,zeroline= False))

        figure=go.Figure(data=data,layout=layout)

        return figure


    def generate_trace_list_linechart(sydney_df_trend, selected_dropdown_value):
        # Make a timeline
        trace_list = []
        for value in selected_dropdown_value:
            selected_value_df = sydney_df_trend[sydney_df_trend['Flight Path']==value]
            trace = go.Scatter(
                x=selected_value_df['Search Date'],
                y=selected_value_df['Current Price AUD'],
                name = value
            )
            trace_list.append(trace)
        return trace_list

    return app
