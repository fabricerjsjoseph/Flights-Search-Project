
def FL03A():
    from FL02_Sydney_Flights_Dataframe import generate_df,generate_master_df_pivot
    import dash
    import dash_table
    from dash.dependencies import Input, Output
    import dash_core_components as dcc
    import dash_html_components as html
    from dash.dash import no_update
    import plotly.graph_objs as go
    from plotly.subplots import make_subplots
    import pandas as pd
    from datetime import date


    # importing data from FL02_Sydney_Flights_Dataframe
    master_df=generate_df()
    flights_count_df=generate_master_df_pivot()


    # Converting Search Date to a datetime object to enable sorting
    master_df['Departure Date']=pd.to_datetime(master_df['Departure Date'],format='%d-%m-%Y').dt.date

    # Sort search date in ascending order
    master_df.sort_values(by='Departure Date',inplace=True)

    # Create today object to extract today's date
    today = date.today()

    # Create dataframe with only today's search result
    master_df_datatable=master_df.copy()

    #Changing date format
    master_df_datatable['Departure Date']=pd.to_datetime(master_df_datatable['Departure Date']).dt.strftime('%d-%m-%Y')

    # Only include latest search date
    master_df_datatable=master_df_datatable[master_df_datatable['Search Date']==today.strftime("%Y-%m-%d")]


    # activate Dash Server
    app = dash.Dash(__name__)

    # Change Flask environment from Production to Development
    #get_ipython().run_line_magic('env', 'FLASK_ENV=development')


    # Create list of flight paths for drop down menu

    destination_list=master_df['Destination'].sort_values().unique()
    flight_path_unique=[]

    for destination in destination_list:
        destination_flight_path_list = master_df[master_df.Destination == destination]['Flight Path'].sort_values().unique()
        flight_path_unique.append(destination_flight_path_list)

    all_options_dict={destination_list[0]:flight_path_unique[0], destination_list[1]:flight_path_unique[1]}



    # Creating the web app layout
    app.layout = html.Div([
        html.Div([
            html.H1('Mauritius-Australia Flights Dashboard'),
            html.H2('Select Destination'),
            dcc.Dropdown(
                id='destination-dropdown',
                options=[{'label': k, 'value': k} for k in all_options_dict.keys()],
                multi=False,
                value='Sydney, Australia'
            ),
            html.H2('Select Flight Path'),
            dcc.Dropdown(
                id='flight-path-dropdown',
                multi=True
            ),
            dcc.Graph(
                id='flights-price-comparison'
            )
        ], style={'width': '55%', 'display': 'inline-block'}),
        html.Div([
            html.H2('Flights Master'),
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {"name": i, "id": i} for i in master_df_datatable.columns
                ],
                data=master_df_datatable.to_dict('records'),
                style_header={'backgroundColor': 'rgb(51, 51, 255)','fontWeight': 'bold','color':'white'},
                style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(204, 204, 255)'}],
                style_cell={'textAlign': 'center'},
                style_cell_conditional=[{'if': {'column_id': c},'textAlign': 'left'} for c in ['Departure Date', 'Flight ID']],
                style_as_list_view=True,
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
                hidden_columns=['Flight Path','Destination','Airline','Search Date']
            ),
            html.Div(id='datatable-interactivity-container'),
        ], style={'width': '35%', 'float': 'right', 'display': 'inline-block','margin-right': '100px','margin-top': '100px'}),
        html.Div([html.H2('Select Flight Path'),
        dcc.Dropdown(id='flight-path-dropdown-2',multi=True)],
        style={'width': '80%','display': 'inline-block','margin-top':'50px','margin-left':'50px'}),
        html.Div([dcc.Graph(id='min-price-trend-graph'),html.P('')
        ], style={'width': '100%','display': 'inline-block'}),
        html.Div([dcc.Graph(id='no-of-flights'),html.P('')
        ], style={'width': '100%','height':'100%','display': 'inline-block'}),
        html.Div(id='none',children=[], style={'display':'none'})
    ])


    ###  CALLBACK TO FILTER DATATABLE
    @app.callback(Output('datatable-interactivity','data'), [Input('destination-dropdown', 'value')])
    def filter_table(selected_destination):
        filtered_datatable_df=master_df_datatable[master_df_datatable.Destination == selected_destination]
        return filtered_datatable_df.to_dict('records')



    ### CALLBACK FOR FLIGHT PATH DROPDOWN MENUS
    # Callback updates available options based on  selected destination
    @app.callback(
        [Output('flight-path-dropdown', 'options'),Output('flight-path-dropdown', 'value')],
        [Input('destination-dropdown', 'value')])
    def set_flight_path_options(selected_destination):
        return [{'label': i, 'value': i} for i in all_options_dict[selected_destination]],[all_options_dict[selected_destination][0]]

    @app.callback(
        [Output('flight-path-dropdown-2', 'options'),Output('flight-path-dropdown-2', 'value')],
        [Input('destination-dropdown', 'value')])
    def set_flight_path_options(selected_destination):
        return [{'label': i, 'value': i} for i in all_options_dict[selected_destination]],all_options_dict[selected_destination]


    ### BARCHART

    @app.callback(Output('flights-price-comparison', 'figure'), [Input('flight-path-dropdown', 'value')])
    def update_bar_graph(selected_dropdown_value):

        if not selected_dropdown_value:
            return no_update

        master_df_barchart=master_df.copy()

        # Only include latest search date
        master_df_barchart=master_df_barchart[master_df_barchart['Search Date']==today.strftime("%Y-%m-%d")]

        # Filter data frame based on flight path
        master_df_barchart = master_df_barchart[(master_df_barchart['Flight Path'].isin(selected_dropdown_value))]

        # Generate trace list and assign to data variable
        data=generate_trace_list_barchart(master_df_barchart, selected_dropdown_value)

        # set up bar chart layout

        layout = go.Layout(barmode = "group", title="Current Price Comparison by Departure Date",
                       xaxis= dict(title= 'Departure Date',ticklen= 5,zeroline= False),
                       yaxis= dict(title= 'AUD',ticklen= 5,zeroline= False))

        # Generate plotly figure object
        figure=go.Figure(data=data,layout=layout)

        # Center title
        figure.update_layout(title_text='<b>Current Price Comparison by Departure Date</b>', title_x=0.5)

        return figure

    def generate_trace_list_barchart(master_df_barchart, selected_dropdown_value):
        # Make a timeline
        trace_list = []
        for value in selected_dropdown_value:
            selected_value_df = master_df_barchart[master_df_barchart['Flight Path']==value]
            trace = go.Bar(
                x=selected_value_df['Departure Date'],
                y=selected_value_df['Current Price AUD'],
                name = value
            )
            trace_list.append(trace)
        return trace_list

    ### LINECHART - PRICE TREND
    @app.callback(Output('min-price-trend-graph', 'figure'), [Input('flight-path-dropdown-2', 'value')])
    def update_linegraph(selected_dropdown_value):

        # Create a copy of source data to filter
        master_df_linechart=master_df.copy()

        master_df_linechart = master_df_linechart[(master_df_linechart['Flight Path'].isin(selected_dropdown_value))]

        master_df_linechart=pd.pivot_table(master_df_linechart,index='Flight Path',columns='Search Date',\
                                              values='Current Price AUD',aggfunc='min')

        master_df_linechart=master_df_linechart.stack().reset_index()
        master_df_linechart.columns=['Flight Path','Search Date','Current Price AUD']

         # Generate trace list and assign to data variable
        data=generate_trace_list_linechart(master_df_linechart, selected_dropdown_value)

        #layout

        layout = go.Layout(barmode = "group", title="Minimum Price Trend by Search Date",
                       xaxis= dict(title= 'Search Date',ticklen= 5,zeroline= False),
                       yaxis= dict(title= 'AUD',ticklen= 5,zeroline= False))

        figure=go.Figure(data=data,layout=layout)

        # Center title
        figure.update_layout(title_text='<b>Minimum Price Trend by Search Date</b>', title_x=0.5)

        return figure


    def generate_trace_list_linechart(master_df_linechart, selected_dropdown_value):
        # Make a timeline
        trace_list = []
        for value in selected_dropdown_value:
            selected_value_df = master_df_linechart[master_df_linechart['Flight Path']==value]
            trace = go.Scatter(x=selected_value_df['Search Date'],y=selected_value_df['Current Price AUD'],name = value)
            trace_list.append(trace)
        return trace_list

    ### LINECHART FOR NO OF FLIGHTS
    @app.callback(Output('no-of-flights', 'figure'), [Input('destination-dropdown', 'value')])
    def update_linegraph_2(selected_destination):
        # Generate trace list and assign to data variable
        data=generate_trace_list_linechart_2(flights_count_df[flights_count_df.Destination == selected_destination],selected_destination)

        figure=make_subplots(rows=len(data),cols=1, subplot_titles=tuple(all_options_dict[selected_destination]))

        for i in range(len(data)):
            figure.add_trace(data[i],row=i+1,col=1)

       # Center and bold title
        figure.update_layout(title_text='<b>Flights Count Trend</b>', title_x=0.5,height=800)

        # set number of ticks on Y xaxis
        figure.update_yaxes(nticks=3)

        return figure

    def generate_trace_list_linechart_2(flights_count_df,selected_destination):

        # Make a timeline
        trace_list = []
        for value in all_options_dict[selected_destination]:
            selected_value_df = flights_count_df[flights_count_df['Flight Path']==value]
            trace = go.Scatter(x=selected_value_df['Search Date'],y=selected_value_df['No of Flights'],name = value)
            trace_list.append(trace)
        return trace_list


    return app

# Assign Dash object to variable app
app=FL03A()

# import webbrowser module
import webbrowser

# Register webbrowser
chrome_path="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
webbrowser.register('chrome', None,webbrowser.BackgroundBrowser(chrome_path))

# Run server
if __name__ == '__main__':
        webbrowser.get('chrome').open_new('http://127.0.0.1:8050/')
        app.run_server(debug=False)
