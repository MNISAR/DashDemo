import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

if __name__=='__main__':
    ###########################
    data = pd.read_csv('nyc_data.csv').reset_index()
    np, cnp, tp, ctp = [], [] , [], []
    for index, row in data.iterrows():
        np.append(int(row['New Positives'].replace(",", '')))
        cnp.append(int(row['Cumulative Number of Positives'].replace(",", "")))
        tp.append(int(row['Total Number of Tests Performed'].replace(",", "")))
        ctp.append(int(row['Cumulative Number of Tests Performed'].replace(",", "")))
    data['New Positives'] = np
    data['Cumulative Number of Positives'] = cnp
    data['Total Number of Tests Performed'] = tp
    data['Cumulative Number of Tests Performed'] = ctp
    all_counties = set([c for c in data['County']])
    dates = [d for d in data['Test Date']]
    min_date, max_date = min(dates), max(dates)

    county_data = {c: data[data['County']==c] for c in all_counties}

    ###########################
    option1 = dcc.Dropdown(
        id='options1',
        options=[{'label':c, 'value':c} for c in county_data.keys()],
        value='Bronx'
    )
    p = html.P(children=["County wise data"])
    fig1 = html.Div(children=[
        dcc.Graph(id='graph1', style={'height': '400px', 'width': '600px'})
    ])
    div1 = html.Div(id='div1', style={'border': '2px solid black', 'float':'left'}, children= [option1, p, fig1])  # daily case line chart

    cols = ['New Positives', 'Cumulative Number of Positives', 'Total Number of Tests Performed', 'Cumulative Number of Tests Performed']
    dwm = ['daily', 'weekly', 'monthly']
    option2 = dcc.Dropdown(
        id='options2',
        options=[{'label':c, 'value':c} for c in dwm],
        value=dwm[0]
    )
    option3 = dcc.Dropdown(
        id='options3',
        options=[{'label':c, 'value':c} for c in cols],
        value=cols[0]
    )
    p = html.P(children=["case bar chart"])
    fig2 = html.Div(children=[
        dcc.Graph(id='graph2', style={'height': '400px', 'width': '600px'})
    ])
    div2 = html.Div(id='div2', style={'border': '2px solid black', 'float':'right'}, children= [option2, option3, p, fig2])  # weekly case bar chart
    br = html.Br()

    f_div = html.Div(id='footer_div', children=[html.P(children=["This is footer"])], style={''})
    footer = html.Footer(children=[f_div])

    app.layout = html.Div(style={'height': '700px', 'width': '1300px'}, children=[div1, div2, br, footer])

    @app.callback(Output('graph1', 'figure'), [Input('options1', 'value')])
    def update_page(county_name):
        print(county_name)
        dates = list(county_data[county_name]['Test Date'])[::-1]
        #print(dates, min_date, max_date)
        
        return {
            'data':[
                {'x': dates,'y': county_data[county_name]['New Positives']},
                {'x': dates,'y': county_data[county_name]['Cumulative Number of Positives']},
                {'x': dates,'y': county_data[county_name]['Total Number of Tests Performed']},
                {'x': dates,'y': county_data[county_name]['Cumulative Number of Tests Performed']}
            ]
        }

    @app.callback(Output('graph2', 'figure'), [Input('options2', 'value'), Input('options3', 'value')])
    def update_page_(dwm, col):
        print(dwm, col)
        if(dwm=='daily'):
            daily_data = data.drop('County', axis=1).groupby(by='Test Date').sum().reset_index()
            return {
                'data': [go.Bar(x=daily_data['Test Date'], y=daily_data[col], name='Daily {}'.format(col))]
            }
        elif(dwm=='weekly'):
            df = data
            df['Test Date'] = pd.to_datetime(df['Test Date']) - pd.to_timedelta(7, unit='d')
            weekly_data = df.groupby(['County', pd.Grouper(key='Test Date', freq='W-MON')])[col].sum().reset_index().groupby('Test Date').sum()
            weekly_data.set_index(pd.Index(['week {}'.format(i) for i in range(len(weekly_data))]), inplace=True)
            #weekly_data = weekly_data.reset_index().sort_values('Test Date')
            return {
                'data': [go.Bar(x=weekly_data.index, y=weekly_data[col], name='Weekly {}'.format(col))]
            }
        else:
            df = data
            df['Test Date'] = pd.to_datetime(df['Test Date']) - pd.to_timedelta(30, unit='d')
            print(df.columns)
            monthly_data = df.groupby(['County', pd.Grouper(key='Test Date', freq='W-MON')])[col].sum().reset_index().groupby('Test Date').sum()
            monthly_data.set_index(pd.Index(['month {}'.format(i) for i in range(len(monthly_data))]), inplace=True)
            print(monthly_data.columns)
            return {
                'data': [go.Bar(x=monthly_data.index, y=monthly_data[col], name='Monthly {}'.format(col))]
            }

    app = dash.Dash(__name__)
    app.run_server()