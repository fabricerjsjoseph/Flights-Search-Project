
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


    # importing data from FL02_Sydney_Flights_Dataframe
    sydney_df=generate_df()


    # Converting Search Date to a datetime object to enable sorting
    sydney_df['Departure Date']=pd.to_datetime(sydney_df['Departure Date'],format='%d-%m-%Y').dt.date

    # Sort search date in ascending order
    sydney_df.sort_values(by='Departure Date',inplace=True)

    # Create today object to extract today's date
    today = date.today()

    # Create dataframe with only today's search result
    sydney_df_datatable=sydney_df.copy()

    #Changing date format
    sydney_df_datatable['Departure Date']=pd.to_datetime(sydney_df_datatable['Departure Date']).dt.strftime('%d-%m-%Y')

    # Only include latest search date
    sydney_df_datatable=sydney_df_datatable[sydney_df_datatable['Search Date']==today.strftime("%Y-%m-%d")]


    # activate Dash Server
    app = dash.Dash(__name__)

    # Change Flask environment from Production to Development
    #get_ipython().run_line_magic('env', 'FLASK_ENV=development')


    # Create list of flight paths for drop down menu
    def flight_paths_dict_list():
        global unique_list
        dictlist = []
        unique_list = sydney_df['Flight Path'].sort_values().unique()
        for flight_path in unique_list:
            dictlist.append({'value': flight_path, 'label': flight_path})
        return dictlist

    dict_flight_paths=flight_paths_dict_list()



    # Creating the web app layout
    app.layout = html.Div([
        html.Div([
            html.H1('MRU-SYD Flights Dashboard'),
            html.H2('Select Flight Path'),
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
            html.H2('Flights Master'),
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {"name": i, "id": i} for i in sydney_df_datatable.columns
                ],
                data=sydney_df_datatable.to_dict('records'),
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
        dcc.Dropdown(id='flight-path-dropdown-2',options=dict_flight_paths,multi=True,value = unique_list)],
        style={'width': '80%','display': 'inline-block','margin-top':'50px','margin-left':'50px'}),
        html.Div([dcc.Graph(id='min-price-trend-graph'),html.P('')
        ], style={'width': '100%','display': 'inline-block'}),
        html.Div(id='hidden-email-alert', style={'display':'none'})
    ])

    ### DATATABLE INTERACTIVITY
    #@app.callback(Output('datatable-interactivity', 'style_data_conditional'),[Input('datatable-interactivity', 'selected_columns')])

    ### BARCHART

    @app.callback(Output('flights-price-comparison', 'figure'), [Input('flight-path-dropdown', 'value')])
    def update_bar_graph(selected_dropdown_value):

        sydney_df_barchart=sydney_df.copy()

        # Only include latest search date
        sydney_df_barchart=sydney_df_barchart[sydney_df_barchart['Search Date']==today.strftime("%Y-%m-%d")]

        # Filter data frame based on flight path
        sydney_df_barchart = sydney_df_barchart[(sydney_df_barchart['Flight Path'].isin(selected_dropdown_value))]

        # Generate trace list and assign to data variable
        data=generate_trace_list_barchart(sydney_df_barchart, selected_dropdown_value)

        # set up bar chart layout

        layout = go.Layout(barmode = "group", title="Current Price Comparison by Departure Date",
                       xaxis= dict(title= 'Departure Date',ticklen= 5,zeroline= False),
                       yaxis= dict(title= 'AUD',ticklen= 5,zeroline= False))

        # Generate plotly figure object
        figure=go.Figure(data=data,layout=layout)

        # Center title
        figure.update_layout(title_text='<b>Current Price Comparison by Departure Date</b>', title_x=0.5)

        return figure

    def generate_trace_list_barchart(sydney_df_barchart, selected_dropdown_value):
        # Make a timeline
        trace_list = []
        for value in selected_dropdown_value:
            selected_value_df = sydney_df_barchart[sydney_df_barchart['Flight Path']==value]
            trace = go.Bar(
                x=selected_value_df['Departure Date'],
                y=selected_value_df['Current Price AUD'],
                name = value
            )
            trace_list.append(trace)
        return trace_list

    ### LINECHART
    @app.callback(Output('min-price-trend-graph', 'figure'), [Input('flight-path-dropdown-2', 'value')])
    def update_linegraph(selected_dropdown_value):

        # Create a copy of source data to filter
        sydney_df_linechart=sydney_df.copy()

        sydney_df_linechart = sydney_df_linechart[(sydney_df_linechart['Flight Path'].isin(selected_dropdown_value))]

        sydney_df_linechart=pd.pivot_table(sydney_df_linechart,index='Flight Path',columns='Search Date',\
                                              values='Current Price AUD',aggfunc='min')

        sydney_df_linechart=sydney_df_linechart.stack().reset_index()
        sydney_df_linechart.columns=['Flight Path','Search Date','Current Price AUD']

         # Generate trace list and assign to data variable
        data=generate_trace_list_linechart(sydney_df_linechart, selected_dropdown_value)

        #layout

        layout = go.Layout(barmode = "group", title="Minimum Price Trend by Search Date",
                       xaxis= dict(title= 'Search Date',ticklen= 5,zeroline= False),
                       yaxis= dict(title= 'AUD',ticklen= 5,zeroline= False))

        figure=go.Figure(data=data,layout=layout)

        # Center title
        figure.update_layout(title_text='<b>Minimum Price Trend by Search Date</b>', title_x=0.5)

        return figure


    def generate_trace_list_linechart(sydney_df_linechart, selected_dropdown_value):
        # Make a timeline
        trace_list = []
        for value in selected_dropdown_value:
            selected_value_df = sydney_df_linechart[sydney_df_linechart['Flight Path']==value]
            trace = go.Scatter(x=selected_value_df['Search Date'],y=selected_value_df['Current Price AUD'],name = value)
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
