import dash
from dash import Dash, dcc, html, callback, Output, Input, State
from pandas.io.formats import style
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import numpy as np
from plotly.subplots import make_subplots


df = pd.read_csv('all_data.csv')

df = df.drop(['Unnamed: 0'], axis=1)


df['attendance'] = np.where((df['product_category'] == 'Pass') & 
                                          (df['product_code'].str.contains('3DAY')), 
                                          3, 
                                          np.where((df['product_category'] == 'Pass') & 
                                                   (df['product_code'].str.contains('4DAY')),
                                                   4,
                                                   np.where((df['product_category'] == 'Pass') & 
                                                            (df['product_code'].str.contains('5DAY')),
                                                            5,
                                                            np.where((df['product_category'] == 'Daily ticket'),
                                                                     1,
                                                                     0))))

###################################################
#               Alap df-ek létrehozása
###################################################

#today = date.today()

x = date(2023,3,22)
today = x  

#mostani év dataframe az event_year alapján
df_current_year = df[df["event_year"] == today.year]

#A days_prior adja vissza, hogy a 0-ik naptól, amikor kezdődik a fesztivál hányadik napnál vagyunk, ezt sok helyen fogjuk felhasználni, mert ez alapján tudjuk
#összevetni a kiválasztott év és az elöző év összevetését is, mivel a dátumok különböznek

#mostani év dataframeben a mai napi days_prior érték
event_year_days_prior = df_current_year['days_prior'].max()

#mostani év dataframeben a legelső days_prior érték
event_year_min_days_prior = df_current_year['days_prior'].min()



################################################### 
#                   Szűrők
###################################################

#dropdown-hoz kell az összes egyedi év
df_unique_year = sorted(df['event_year'].unique(), reverse=True)

#dropdown-ban melyik év legyen kiválasztva default-nak a Previous Year-nél, ez mindig a mostani évhez képest elöző lesz
prev_year = df_unique_year[1]

#A radio button-ok értékei, label a látható megnevezés, a value pedig a dataframe oszlopát jelöli, kivéve a quantity-nél
options = [
    {'label': ' Net amount', 'value': 'net_amount_huf'},
    {'label': ' Gross amount', 'value': 'gross_amount_huf'},
    {'label': ' Quantity', 'value': 'transaction_id'},
    {'label': ' Attendance', 'value': 'attendance'}
]


###################################################
#                        Html
###################################################


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

app.layout = html.Div(children=[

    #bullet chart-ok
    html.Div([
            dbc.Row([
                dbc.Col([
                        html.Div([
                            dcc.Graph( id='fig_bullet', config = {'displayModeBar': False})
                ],className='bullets')
                    ],  width={"size": 2, "offset": 1}),
                dbc.Col([
                        html.Div([
                            dcc.Graph( id='fig_bullet_days', config = {'displayModeBar': False})
                ],className='bullets')
                    ], width=2),
                dbc.Col([
                        html.Div([
                            dcc.Graph( id='fig_bullet_pass', config = {'displayModeBar': False})
                ],className='bullets')
                    ], width=2),    
            ]   
            ),
    ]),

    #szűrők
    dbc.Row([
        #Év választók
        dbc.Col([
            html.Div([
                html.H6('Selected year'),
                dcc.Dropdown(df_unique_year, today.year, multi=False, id='selected_year_dd')
            ]),
            html.Div([
                html.H6('Previous year'),
                dcc.Dropdown(df_unique_year, prev_year, multi=False, id='previous_year_dd')
            ]),
        ], width=2),
        #Radio button-ok, nettó-bruttó-dbszám-látógatószám
        dbc.Col([
            html.Div([
                dcc.RadioItems(options=options, 
                value='net_amount_huf',  labelStyle={'display': 'block'}, id='radio')
            ]),
        ], width=2, align="center"),
        #Napok csúszkája
        dbc.Col([
            html.Div([
                dcc.RangeSlider(event_year_min_days_prior, 0, value=[event_year_min_days_prior, event_year_days_prior], id='my-range-slider', tooltip={"placement": "bottom", "always_visible": True}),
                html.Div(id='range-slider')
            ]),
        ], width=6, align="end"),
    ], justify="center", style={'margin-top':'20px'}),


    #Össz KPI+diagrammok
    html.Div([
            dbc.Row([
                dbc.Col([

                        #KPI
                        dbc.Card([
                            html.Div(id='filtered_kpi')
                        ], color="#e3f1fe", inverse=True, className='kpi'),

                        #Oszlopdiagram
                        html.Div(
                            dcc.Graph(id='fig_bar', config={'displayModeBar': False}),
                            className='graf'
                        )
                    ], width={"size": 4, "offset": 1}),

                #Vonaldiagram
                dbc.Col(
                        html.Div(
                            dcc.Graph( id='fig_line', config = {'displayModeBar': False}),
                            className='graf',
                        )
                    ,width=6)           
            ]   
            ),
    ], className='all_part'),

    #Pass KPI+diagrammok
    html.Div([
            dbc.Row([
                dbc.Col([

                        #KPI
                        dbc.Card([
                            html.Div(id='filtered_pass_kpi')
                        ], color="#eadafe", inverse=True, className='kpi'),

                        #Oszlopdiagram
                        html.Div(
                            dcc.Graph(id='fig_bar_pass', config={'displayModeBar': False}),
                            className='graf'
                        )
                    ], width={"size": 4, "offset": 1}),

                #Vonaldiagram
                dbc.Col(
                        html.Div(
                            dcc.Graph( id='fig_line_pass', config = {'displayModeBar': False}),
                            className='graf',
                        )
                    ,width=6)           
            ]   
            )
    ], className='all_part'),

    #Daily ticket KPI+diagrammok
    html.Div([
            dbc.Row([
                dbc.Col([

                        #KPI
                        dbc.Card([
                            html.Div(id='filtered_days_kpi')
                        ], color="#f8e9e2", inverse=True, className='kpi'),

                        #Oszlopdiagram
                        html.Div(
                            dcc.Graph(id='fig_bar_days', config={'displayModeBar': False}),
                            className='graf'
                        )
                    ], width={"size": 4, "offset": 1}),

                #Vonaldiagram
                dbc.Col(
                        html.Div(
                            dcc.Graph( id='fig_line_days', config = {'displayModeBar': False}),
                            className='graf',
                        )
                    ,width=6)
                 ]   
            ),
    ], className='all_part'),

])


#A Callback Output-jaiban vannak benne azok az elemek, amiknek a szűrők használatával változniuk kell
#Az Input-ban pedig a szűrők vannak, amik alapján fognak változni

@callback(
    [Output('filtered_kpi', 'children'), Output('filtered_days_kpi', 'children'), Output('filtered_pass_kpi', 'children'),
    Output('fig_line', 'figure'), Output('fig_line_days', 'figure'), Output('fig_line_pass', 'figure'), Output('fig_bar', 'figure'), 
    Output('fig_bar_days', 'figure'), Output('fig_bar_pass', 'figure'), Output('range-slider', 'children'),Output('fig_bullet', 'figure'),
    Output('fig_bullet_days', 'figure'), Output('fig_bullet_pass', 'figure')], 

    [Input('selected_year_dd', 'value'), Input('previous_year_dd', 'value'), Input('my-range-slider', 'value'), Input('radio', 'value'),],
)

   
#A függvény, ami változtatja az elemeket, a paraméterei az Inputban látható szűrők megnevezései

def update_charts(year_selected, prev_year, range_value, radio_value):

    ############################
    #       alap df-ek
    ############################

    #Szűrő alapján kiválasztott fő év
    df_current_year = df[df["event_year"] == year_selected]

    #Kiválasztott fő év max days_prior értéke, rangeslider alapján hozza
    event_year_days_prior = range_value[1]

    #Kiválasztott fő év min days_prior értéke, rangeslider alapján hozza
    event_year_min_days_prior = range_value[0]

    #Korábbi választott év
    df_py = df[df["event_year"] == prev_year] 

    #Korábbi választott év days_prior értéke a kiválasztott fő év days_prior max és min értéke között legyen, hogy össze tudjuk vetni a kettőt
    df_py_daysprior = df_py[(df_py["days_prior"] <= event_year_days_prior) & (df_py["days_prior"] >= event_year_min_days_prior)] 

    #A fő évnél is a days_pior range meghatározása
    df_cy_daysprior = df_current_year[(df_current_year["days_prior"] <= event_year_days_prior) & (df_current_year["days_prior"] >= event_year_min_days_prior)] 

    ############################
    #    napi jegyekhez df-ek
    ############################

    #Napi jegyekre szűrése a fő évnél és a korábbi évnél
    df_cy_days = df_cy_daysprior[df_cy_daysprior["product_category"] == 'Daily ticket'] 
    df_py_daysprior_days = df_py_daysprior[df_py_daysprior["product_category"] == 'Daily ticket'] 

    ############################
    #     bérletekhez df-ek
    ############################

    #Bérletekre szűrése a fő évnél és a korábbi évnél
    df_cy_pass = df_cy_daysprior[df_cy_daysprior["product_category"] == 'Pass'] 
    df_py_daysprior_pass = df_py_daysprior[df_py_daysprior["product_category"] == 'Pass'] 


    #Ft vagy pcs legyen a mennyiség
    unit = 'Pcs' if radio_value == 'attendance'  or radio_value == 'transaction_id' else 'Ft'


    #Itt is fel kellett venni az options-okat, hogy ki tudjuk szedni a label-eket is, mert a paraméterben csak a radio_value fog jönni, a label nem
    options = [
        {'label': ' Net amount', 'value': 'net_amount_huf'},
        {'label': ' Gross amount', 'value': 'gross_amount_huf'},
        {'label': ' Quantity', 'value': 'transaction_id'},
        {'label': ' Attendance', 'value': 'attendance'}
    ]

    #Itt kapjuk meg az összes radio button elem label-jét is nem csak a value-ját
    selected_label = [o['label'] for o in options if o['value'] == radio_value.lower()][0]

    
    ###############################
    #            KPI-ok
    ###############################

    ##################
    #   Összes
    ##################

    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        cy_sum_filtered_all = int(df_cy_daysprior[radio_value].sum())
        py_filtered_all =  int(df_py_daysprior[radio_value].sum()) 

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        cy_sum_filtered_all = df_cy_daysprior[radio_value].count()
        py_filtered_all =  df_py_daysprior[radio_value].count()


    #bevétel különbség
    py_vs_now_net_all = cy_sum_filtered_all - py_filtered_all

    #százalékos eltérés számolása
    percentage_net_all = py_vs_now_net_all / (cy_sum_filtered_all / 100)

    ##################
    #   Napi jegyek
    ##################

    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        cy_sum_filtered_days = int(df_cy_days.loc[df_cy_days['event_year'] == year_selected, radio_value].sum())
        py_filtered_days =  int(df_py_daysprior_days[radio_value].sum()) 

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        cy_sum_filtered_days = int(df_cy_days.loc[df_cy_days['event_year'] == year_selected, radio_value].count())
        py_filtered_days =  int(df_py_daysprior_days[radio_value].count()) 
        


    #bevétel különbség
    py_vs_now_net_days = cy_sum_filtered_days - py_filtered_days

    #százalékos eltérés számolása
    percentage_net_days = py_vs_now_net_days / (cy_sum_filtered_days / 100)

    ##################
    #    Bérletek
    ##################

    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        cy_sum_filtered_pass = int(df_cy_pass.loc[df_cy_pass['event_year'] == year_selected, radio_value].sum())
        py_filtered_pass =  int(df_py_daysprior_pass[radio_value].sum()) 

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        cy_sum_filtered_pass = int(df_cy_pass.loc[df_cy_pass['event_year'] == year_selected, radio_value].count())
        py_filtered_pass =  int(df_py_daysprior_pass[radio_value].count()) 

    #bevétel különbség
    py_vs_now_net_pass = cy_sum_filtered_pass - py_filtered_pass

    #százalékos eltérés számolása
    percentage_net_pass = py_vs_now_net_pass / (cy_sum_filtered_pass / 100)

    ##################
    #   HTML elemek
    ##################

    #A KPI-oknál ha negatív a bevétel különbség, akkor az a html oldal stílusában is látszódjon, így akkor pirossal és egy lefele mutató nyíllal jelöljük, ellenkező esetben pedig
    #zölddel és felfele mutató nyíllal
    colors = ['danger' if x < 0 else 'success' for x in [py_vs_now_net_all, py_vs_now_net_days, py_vs_now_net_pass]]
    icon = ['bi bi-arrow-down-circle mx-3' if x < 0 else 'bi bi-arrow-up-circle mx-3' for x in [py_vs_now_net_all, py_vs_now_net_days, py_vs_now_net_pass]]


    #Maguk a KPI-ok meghatározása, amik id alapján bekerülnek a html-be
    #Mind Card elemek, CardHeader-rel, ami a címet adja meg és CardBody-val, ami a már kiszámolt összeget megjelenítését adja a kiválaszott évre és a korábbi évre is

    filtered_kpi = html.Div(
        [
            dbc.CardHeader(html.H4('Total '+selected_label, className="text-center")),
            dbc.CardBody([html.H3(
                f"{cy_sum_filtered_all:,} {'Pcs' if radio_value == 'attendance' or radio_value == 'transaction_id' else 'Ft'}", className="card-text text-center",
            ),
            html.H6(
                [
                    f"{py_vs_now_net_all:,} {'Pcs' if radio_value == 'attendance' or radio_value == 'transaction_id' else 'Ft'}",
                    html.I(className=f"text-{icon[0]}"), f"{round(percentage_net_all, 2)}%",
                ],
                className=f"text-{colors[0]}",
            ),])
        ]
    )

    filtered_days_kpi = html.Div(
        [
            dbc.CardHeader(html.H4('Daily Ticket '+selected_label, className="text-center")),
            dbc.CardBody([html.H3(
                f"{cy_sum_filtered_days:,} {'Pcs' if radio_value == 'attendance' or radio_value == 'transaction_id' else 'Ft'}", className="card-text text-center",
            ),
            html.H6(
                [
                    f"{py_vs_now_net_days:,} {'Pcs' if radio_value == 'attendance' or radio_value == 'transaction_id' else 'Ft'}",
                      html.I(className=f"text-{icon[1]}"), f"{round(percentage_net_days, 2)}%",
                ],
                className=f"text-{colors[1]}",
            ),])
        ]
    )

    filtered_pass_kpi = html.Div(
        [
            dbc.CardHeader(html.H4('Pass '+selected_label, className="text-center")),
            dbc.CardBody([html.H3(
                f"{cy_sum_filtered_pass:,} {'Pcs' if radio_value == 'attendance' or radio_value == 'transaction_id' else 'Ft'}", className="card-text text-center",
            ),
            html.H6(
                [
                    f"{py_vs_now_net_pass:,} {'Pcs' if radio_value == 'attendance' or radio_value == 'transaction_id' else 'Ft'}",
                      html.I(className=f"text-{icon[2]}"), f"{round(percentage_net_pass, 2)}%",
                ],
                className=f"text-{colors[2]}",
            ),])
        ]
    )


    ###############################
    #         bullet charts
    ###############################


    ##################
    #     Összes
    ##################

    #Hasonlóan mint a KPI-nál, ha a kiválasztott év összege nagyobb mint a korábbi válaszott évé-é, akkor zöld színt használjon, amúgy meg pirosat
    if cy_sum_filtered_all > py_filtered_all:
        bar_color = "green"
    else:
        bar_color = "red"
    
    #itt használjuk a make_subplots-ot, hogy egyszerre két grafikont tudjunk ábrázolni, amik egy y és x tengelyen vannak
    fig_bullet = make_subplots(shared_yaxes=True, shared_xaxes=True)

    #ez a korábbi választott év fektetett diagram meghatározása, a hovertemplate-ben az aktuális összeg fog kiírodni
    fig_bullet.add_bar(x=[py_filtered_all], y=[0,1], opacity=0.6, width=0.7, marker=dict(color='gray'), 
                       hovertemplate=f"{selected_label} {prev_year}: %{{y:,}} {unit}" if py_filtered_all/1000000 < 1 else f"{selected_label} {prev_year}: {py_filtered_all/1000000:,.2f} M {unit}<br>",
                       hoverinfo='text', name ='',orientation='h')
    
    #ez a választott év fektetett diagram meghatározása, a hovertemplate-ben az aktuális összeg fog kiírodni
    fig_bullet.add_bar(x=[cy_sum_filtered_all], y=[0,1], width=0.3, marker=dict(color=bar_color), 
                       hovertemplate=f"{selected_label} {year_selected}: %{{y:,}} {unit}" if cy_sum_filtered_all/1000000 < 1 else f"{selected_label} {year_selected}: {cy_sum_filtered_all/1000000:,.2f} M {unit}<br>",
                       hoverinfo='text', name ='',orientation='h')
    
    #Megadjuk a dizájn elemeket és a címet
    fig_bullet.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#eff5fe',
        paper_bgcolor='#eff5fe',
        showlegend=False,
        #width=800,
        height=150,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(size=14, color='#7b9cc2'),
        title={
            'text': "Total",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        barmode='overlay'
    )



    ##################
    #   napi jegyek
    ##################

    #Hasonlóan mint a KPI-nál, ha a kiválasztott év összege nagyobb mint a korábbi válaszott évé-é, akkor zöld színt használjon, amúgy meg pirosat
    if cy_sum_filtered_days > py_filtered_days:
        bar_color = "green"
    else:
        bar_color = "red"

    #itt használjuk a make_subplots-ot, hogy egyszerre két grafikont tudjunk ábrázolni, amik egy y és x tengelyen vannak
    fig_bullet_days = make_subplots(shared_yaxes=True, shared_xaxes=True)

    #ez a korábbi választott év fektetett diagram meghatározása, a hovertemplate-ben az aktuális összeg fog kiírodni
    fig_bullet_days.add_bar(x=[py_filtered_days], y=[0,1], opacity=0.6, width=0.7, marker=dict(color='gray'),
                       hovertemplate=f"{selected_label} {prev_year}: %{{y:,}} {unit}" if py_filtered_days/1000000 < 1 else f"{selected_label} {prev_year}: {py_filtered_days/1000000:,.2f} M {unit}<br>",
                       hoverinfo='text', name ='',orientation='h')
    
    #ez a választott év fektetett diagram meghatározása, a hovertemplate-ben az aktuális összeg fog kiírodni
    fig_bullet_days.add_bar(x=[cy_sum_filtered_days], y=[0,1], width=0.3, marker=dict(color=bar_color),
                       hovertemplate=f"{selected_label} {year_selected}: %{{y:,}} {unit}" if cy_sum_filtered_days/1000000 < 1 else f"{selected_label} {year_selected}: {cy_sum_filtered_days/1000000:,.2f} M {unit}<br>",
                       hoverinfo='text', name ='',orientation='h')

    #Megadjuk a dizájn elemeket és a címet
    fig_bullet_days.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#eff5fe',
        paper_bgcolor='#eff5fe',
        showlegend=False,
        #width=800,
        height=150,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(size=14, color='#7b9cc2'),
        title={
            'text': "Daily ticket",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        barmode='overlay'
    )


    ##################
    #     bérletek
    ##################

    #Hasonlóan mint a KPI-nál, ha a kiválasztott év összege nagyobb mint a korábbi válaszott évé-é, akkor zöld színt használjon, amúgy meg pirosat
    if cy_sum_filtered_pass > py_filtered_pass:
        bar_color = "green"
    else:
        bar_color = "red"

    #itt használjuk a make_subplots-ot, hogy egyszerre két grafikont tudjunk ábrázolni, amik egy y és x tengelyen vannak
    fig_bullet_pass = make_subplots(shared_yaxes=True, shared_xaxes=True)

    #ez a korábbi választott év fektetett diagram meghatározása, a hovertemplate-ben az aktuális összeg fog kiírodni
    fig_bullet_pass.add_bar(x=[py_filtered_pass], y=[0,1], opacity=0.6, width=0.7, marker=dict(color='gray'),
                       hovertemplate=f"{selected_label} {prev_year}: %{{y:,}} {unit}" if py_filtered_pass/1000000 < 1 else f"{selected_label} {prev_year}: {py_filtered_pass/1000000:,.2f} M {unit}<br>",
                       hoverinfo='text', name ='',orientation='h')
    
    #ez a választott év fektetett diagram meghatározása, a hovertemplate-ben az aktuális összeg fog kiírodni
    fig_bullet_pass.add_bar(x=[cy_sum_filtered_pass], y=[0,1], width=0.3, marker=dict(color=bar_color),
                       hovertemplate=f"{selected_label} {year_selected}: %{{y:,}} {unit}" if cy_sum_filtered_pass/1000000 < 1 else f"{selected_label} {year_selected}: {cy_sum_filtered_pass/1000000:,.2f} M {unit}<br>",
                       hoverinfo='text', name ='',orientation='h')

    #Megadjuk a dizájn elemeket és a címet
    fig_bullet_pass.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#eff5fe',
        paper_bgcolor='#eff5fe',
        showlegend=False,
        #width=800,
        height=150,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(size=14, color='#7b9cc2'),
        title={
            'text': "Pass",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        barmode='overlay'
    )



    ###############################
    #         Vonaldiagram
    ###############################

    ##################
    #     Összes
    ##################

    fig_line = go.Figure()

    #ly - Last Year
    df_py_fig_all = df_py_daysprior

    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        #A kiválasztott radio button alapján összegezzük és group by-oljuk days_prior alapján
        df_py_sum_fig_all = df_py_fig_all.groupby(by="days_prior")[radio_value].sum()

        df_py_sum_fig_all = df_py_sum_fig_all.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_py_sum_fig_all.rename(columns={"days_prior":"Days Prior", radio_value:selected_label},inplace=True)

        #létrehozzuk az első vonaldiagrammot, aminél lesz egy fill paraméter, hogy kitöltse színnel a vonaldiagramm alatti területet, illetve itt is van egy hovertemaplate, ami kiírja az összeget
        fig_line.add_trace(go.Scatter( x=df_py_sum_fig_all['Days Prior'], y=(df_py_sum_fig_all[selected_label]), fill = 'tozeroy', name = '',
                                fillcolor='#bcddf9',  line=dict(color='#bcddf9'), hovertemplate=f'{selected_label} {prev_year}: %{{y:,.0f}} {unit} <br>'))
        

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        #transaction_id alapján count-oljuk és group by-oljuk days_prior alapján
        df_py_sum_fig_all = df_py_fig_all.groupby(by="days_prior")[radio_value].count()

        df_py_sum_fig_all = df_py_sum_fig_all.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_py_sum_fig_all.rename(columns={"days_prior":"Days Prior", radio_value:'Transaction Id'},inplace=True)

        #létrehozzuk az első vonaldiagrammot, aminél lesz egy fill paraméter, hogy kitöltse színnel a vonaldiagramm alatti területet, illetve itt is van egy hovertemaplate, ami kiírja az összeget
        fig_line.add_trace(go.Scatter( x=df_py_sum_fig_all['Days Prior'], y=(df_py_sum_fig_all['Transaction Id']), fill = 'tozeroy', name = '',
                                fillcolor='#bcddf9',  line=dict(color='#bcddf9'), hovertemplate=f'Quantity {prev_year}: %{{y:,.0f}} {unit} <br>'))




    #cy - Current Year
    df_cy_fig_all = df_cy_daysprior

    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        #A kiválasztott radio button alapján összegezzük és group by-oljuk days_prior alapján
        df_cy_sum_fig_all = df_cy_fig_all.groupby(by="days_prior")[radio_value].sum()

        df_cy_sum_fig_all = df_cy_sum_fig_all.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_cy_sum_fig_all.rename(columns={"days_prior":"Days Prior", radio_value:selected_label},inplace=True)

        #létrehozzuk a második vonaldiagrammot, aminél szintén van egy hovertemaplate, ami kiírja az összeget
        fig_line.add_trace(go.Scatter(x=df_cy_sum_fig_all['Days Prior'], y=(df_cy_sum_fig_all[selected_label]), name='', line=dict(color='#5fc8ff'), 
                                hovertemplate=f'{selected_label} {year_selected}: %{{y:,.0f}} {unit} <br>'))


    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        #transaction_id alapján count-oljuk és group by-oljuk days_prior alapján
        df_cy_sum_fig_all = df_cy_fig_all.groupby(by="days_prior")[radio_value].count()

        df_cy_sum_fig_all = df_cy_sum_fig_all.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_cy_sum_fig_all.rename(columns={"days_prior":"Days Prior", radio_value:'Transaction Id'},inplace=True)

        #létrehozzuk a második vonaldiagrammot, aminél szintén van egy hovertemaplate, ami kiírja az összeget
        fig_line.add_trace(go.Scatter(x=df_cy_sum_fig_all['Days Prior'], y=(df_cy_sum_fig_all['Transaction Id']), name='', line=dict(color='#5fc8ff'), 
                                hovertemplate=f'Quantity {year_selected}: %{{y:,.0f}} {unit} <br>'))

    #Megadjuk a dizájn elemeket
    fig_line.update_layout(
        plot_bgcolor='#eff5fe',  # Set the background color of the plot
        paper_bgcolor='#eff5fe',  # Set the background color of the paper
        showlegend=False, 
        xaxis=dict(showgrid=False, zeroline=False), 
        yaxis=dict(showgrid=False, zeroline=False),
        #width=800, 
        height=260,  
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(size=14,color='#7b9cc2')
    )

    #megadjuk, hogy közös x tengelyen legyenek
    fig_line.update_layout(hovermode='x unified', hoverlabel=dict(bgcolor='white', font_size=12))


    ##################
    #   Napi jegyek
    ##################

    fig_line_days = go.Figure()

    #ly - Last Year
    df_py_fig_days = df_py_daysprior_days

    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        #A kiválasztott radio button alapján összegezzük és group by-oljuk days_prior alapján
        df_py_sum_fig_days = df_py_fig_days.groupby(by="days_prior")[radio_value].sum()

        df_py_sum_fig_days = df_py_sum_fig_days.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_py_sum_fig_days.rename(columns={"days_prior":"Days Prior", radio_value:selected_label},inplace=True)

        fig_line_days.add_trace(go.Scatter( x=df_py_sum_fig_days['Days Prior'], y=(df_py_sum_fig_days[selected_label]), fill = 'tozeroy', name = '', fillcolor='#fad2b6', 
                                        line=dict(color='#fad2b6'),  hovertemplate=f'{selected_label} {prev_year}: %{{y:,.0f}} {unit} <br>')) 

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        #transaction_id alapján count-oljuk és group by-oljuk days_prior alapján
        df_py_sum_fig_days = df_py_fig_days.groupby(by="days_prior")[radio_value].count()

        df_py_sum_fig_days = df_py_sum_fig_days.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_py_sum_fig_days.rename(columns={"days_prior":"Days Prior", radio_value:'Transaction Id'},inplace=True)

        fig_line_days.add_trace(go.Scatter( x=df_py_sum_fig_days['Days Prior'], y=(df_py_sum_fig_days['Transaction Id']), fill = 'tozeroy', name = '', fillcolor='#fad2b6', 
                                        line=dict(color='#fad2b6'),  hovertemplate=f'Quantity {prev_year}: %{{y:,.0f}} {unit} <br>')) 


    #cy - Current Year
    df_cy_fig_days = df_cy_days

    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        #A kiválasztott radio button alapján összegezzük és group by-oljuk days_prior alapján
        df_cy_sum_fig_days = df_cy_fig_days.groupby(by="days_prior")[radio_value].sum()

        df_cy_sum_fig_days = df_cy_sum_fig_days.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_cy_sum_fig_days.rename(columns={"days_prior":"Days Prior", radio_value:selected_label},inplace=True)

        #létrehozzuk a második vonaldiagrammot, aminél szintén van egy hovertemaplate, ami kiírja az összeget
        fig_line_days.add_trace(go.Scatter(x=df_cy_sum_fig_all['Days Prior'], y=(df_cy_sum_fig_days[selected_label]), name='', line=dict(color='#f7ad89'),
                                        hovertemplate=f'{selected_label} {year_selected}: %{{y:,.0f}} {unit} <br>'))


    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        #transaction_id alapján count-oljuk és group by-oljuk days_prior alapján
        df_cy_sum_fig_days = df_cy_fig_days.groupby(by="days_prior")[radio_value].count()

        df_cy_sum_fig_days = df_cy_sum_fig_days.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_cy_sum_fig_days.rename(columns={"days_prior":"Days Prior", radio_value:'Transaction Id'},inplace=True)

        #létrehozzuk a második vonaldiagrammot, aminél szintén van egy hovertemaplate, ami kiírja az összeget
        fig_line_days.add_trace(go.Scatter(x=df_cy_sum_fig_all['Days Prior'], y=(df_cy_sum_fig_days['Transaction Id']), name='', line=dict(color='#f7ad89'),
                                        hovertemplate=f'Quantity {year_selected}: %{{y:,.0f}} {unit} <br>'))


    #Megadjuk a dizájn elemeket
    fig_line_days.update_layout(
        plot_bgcolor='#f7f0ee',  # Set the background color of the plot
        paper_bgcolor='#f7f0ee',  # Set the background color of the paper
        showlegend=False, 
        xaxis=dict(showgrid=False, zeroline=False), 
        yaxis=dict(showgrid=False, zeroline=False),
        #width=800, 
        height=260,  
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(size=14,color='#f4c093')
    )

    #megadjuk, hogy közös x tengelyen legyenek
    fig_line_days.update_layout(hovermode='x unified', hoverlabel=dict(bgcolor='white', font_size=12))


    ##################
    #    Bérletek
    ##################
    fig_line_pass = go.Figure()

    #ly - Last Year
    df_py_fig_pass = df_py_daysprior_pass

    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        #A kiválasztott radio button alapján összegezzük és group by-oljuk days_prior alapján
        df_py_sum_fig_pass = df_py_fig_pass.groupby(by="days_prior")[radio_value].sum()

        df_py_sum_fig_pass = df_py_sum_fig_pass.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_py_sum_fig_pass.rename(columns={"days_prior":"Days Prior", radio_value:selected_label},inplace=True)

        fig_line_pass.add_trace(go.Scatter( x=df_py_sum_fig_pass['Days Prior'], y=(df_py_sum_fig_pass[selected_label]), fill = 'tozeroy', name = '', fillcolor='#dab0ff',
                                            line=dict(color='#dab0ff'),  hovertemplate=f'{selected_label} {prev_year}: %{{y:,.0f}} {unit} <br>')) 

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        #transaction_id alapján count-oljuk és group by-oljuk days_prior alapján
        df_py_sum_fig_pass = df_py_fig_pass.groupby(by="days_prior")[radio_value].count()

        df_py_sum_fig_pass = df_py_sum_fig_pass.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_py_sum_fig_pass.rename(columns={"days_prior":"Days Prior", radio_value:'Transaction Id'},inplace=True)

        fig_line_pass.add_trace(go.Scatter( x=df_py_sum_fig_pass['Days Prior'], y=(df_py_sum_fig_pass['Transaction Id']), fill = 'tozeroy', name = '', fillcolor='#dab0ff',
                                            line=dict(color='#dab0ff'),  hovertemplate=f'Quantity {prev_year}: %{{y:,.0f}} {unit} <br>')) 


    #cy - Current Year
    df_cy_fig_pass = df_cy_pass

    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        #A kiválasztott radio button alapján összegezzük és group by-oljuk days_prior alapján
        df_cy_sum_fig_pass = df_cy_fig_pass.groupby(by="days_prior")[radio_value].sum()

        df_cy_sum_fig_pass = df_cy_sum_fig_pass.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_cy_sum_fig_pass.rename(columns={"days_prior":"Days Prior", radio_value:selected_label},inplace=True)

        #létrehozzuk a második vonaldiagrammot, aminél szintén van egy hovertemaplate, ami kiírja az összeget
        fig_line_pass.add_trace(go.Scatter(x=df_cy_sum_fig_pass['Days Prior'], y=(df_cy_sum_fig_pass[selected_label]), name='', line=dict(color='#aa55ff'),
                                        hovertemplate=f'{selected_label} {year_selected}: %{{y:,.0f}} {unit} <br>')) 

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        #transaction_id alapján count-oljuk és group by-oljuk days_prior alapján
        df_cy_sum_fig_pass = df_cy_fig_pass.groupby(by="days_prior")[radio_value].count()

        df_cy_sum_fig_pass = df_cy_sum_fig_pass.to_frame().reset_index()

        #A megjelenített címek miatt átlakítjuk az oszlop címeket
        df_cy_sum_fig_pass.rename(columns={"days_prior":"Days Prior", radio_value:'Transaction Id'},inplace=True)

        #létrehozzuk a második vonaldiagrammot, aminél szintén van egy hovertemaplate, ami kiírja az összeget
        fig_line_pass.add_trace(go.Scatter(x=df_cy_sum_fig_pass['Days Prior'], y=(df_cy_sum_fig_pass['Transaction Id']), name='', line=dict(color='#aa55ff'),
                                        hovertemplate=f'Quantity {year_selected}: %{{y:,.0f}} {unit} <br>')) 


    #Megadjuk a dizájn elemeket
    fig_line_pass.update_layout(
        plot_bgcolor='#f3ebfe',  # Set the background color of the plot
        paper_bgcolor='#f3ebfe',  # Set the background color of the paper
        showlegend=False, 
        xaxis=dict(showgrid=False, zeroline=False), 
        yaxis=dict(showgrid=False, zeroline=False),
        #width=800, 
        height=260,  
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(size=14,color='#cdadcb')
    )

    #megadjuk, hogy közös x tengelyen legyenek
    fig_line_pass.update_layout(hovermode='x unified', hoverlabel=dict(bgcolor='white', font_size=12))




    
    ###############################
    #        Oszlopdiagram
    ###############################


    ##################
    #     Összes
    ##################


    fig_bar = go.Figure()

    df_fig_bar = df_cy_daysprior

    # Dataframe amiben a hónapok és 0-s értékek vannak, majd ezeket a 0-kat fogjuk feltölteni értékekkel
    df_months = pd.DataFrame({
        'month': ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
        radio_value: [0,0, 0, 0, 0, 0, 0, 0, 0]
    })

    #átalakítjuk a create_time mezőt datetime típusuvá
    df_fig_bar['create_time'] = pd.to_datetime(df_fig_bar['create_time'])

    #kivesszük a create_time-ból a hónapok neveit
    df_fig_bar['month'] = df_fig_bar['create_time'].dt.strftime('%b')



    #Prev year az összehasonlításos tooltip-hez ezek az adatok is kellenek
    df_py_fig_bar = df_py_daysprior

    #átalakítjuk a create_time mezőt datetime típusuvá
    df_py_fig_bar['create_time'] = pd.to_datetime(df_py_fig_bar['create_time'])

    #kivesszük a create_time-ból a hónapok neveit
    df_py_fig_bar['month'] = df_py_fig_bar['create_time'].dt.strftime('%b')  



    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        monthly_net = df_fig_bar.groupby(['month'])[radio_value].sum().reset_index()

        #elöző kiválasztott év
        monthly_net_py = df_py_fig_bar.groupby(['month'])[radio_value].sum().reset_index()

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        monthly_net = df_fig_bar.groupby(['month'])[radio_value].count().reset_index()

        #elöző kiválasztott év
        monthly_net_py = df_py_fig_bar.groupby(['month'])[radio_value].count().reset_index()


    df_monthly_net = pd.DataFrame({
        'month': monthly_net['month'],
        radio_value: monthly_net[radio_value]
    })

    # Mergel-jük az eredeti dataframe-t a most létrejövővel
    df_result = pd.merge(df_months, df_monthly_net, on='month', how='left')

    # A Null-os értékeket cseréljük 0-ra
    df_result.fillna(0, inplace=True)

    #a merge-lés miatt a radio_value_y változata kell
    df_result = pd.concat([df_result['month'], df_result[radio_value+'_y']], axis=1)
    df_result.columns = ['month', radio_value]

    #létrejön a dataframe-ünk, amivel már tudunk mutatni adatokat
    df_py_monthly_net = pd.DataFrame({
        'month': monthly_net['month'],
        radio_value: monthly_net_py[radio_value]
    })

    # Mergel-jük az eredeti dataframe-t a most létrejövővel
    df_py_result = pd.merge(df_months, df_py_monthly_net, on='month', how='left')

    # A Null-os értékeket cseréljük 0-ra
    df_py_result.fillna(0, inplace=True)

    #a merge-lés miatt a radio_value_y változata kell
    df_py_result = pd.concat([df_py_result['month'], df_py_result[radio_value+'_y']], axis=1)
    df_py_result.columns = ['month', radio_value]

    #A megjelenítés miatt az adatok kétszeresét elmentjük
    max_value = df_result[radio_value].max() * 2

    # Létrehozzuk az oszlopdiagrammot, a text az oszlopok feletti szöveg lesz, aminél van plusz formázás, hogyha milliós a szám vagy hogyha nem az, illetve van egy hovertemplate, 
    # #aminél megjelenik a korábbi választott és és a választott év összegei
    fig_bar = go.Figure(go.Bar(
        x=df_result['month'],
        y=df_result[radio_value],
        marker_color='#5fc8ff',
        text=[f"{value:.2f}" if value/1000000 < 1 else f"{value/1000000:,.2f} M" for value in df_result[radio_value]],
        textposition='outside',
        textangle=0,
        name='',
        hovertemplate='<b>%{x}</b><br>' + 
        f'{year_selected}: %{{y:,.0f}} {unit}<br>' +
        f'{prev_year}: %{{customdata[0]:,.0f}} {unit}',
        customdata=[[df_py_result[radio_value][i]] for i in range(len(df_py_result))]
    ))


    #Megadjuk a dizájn elemeket
    fig_bar.update_layout(
        xaxis_title='Month',
        yaxis_title=selected_label,
        plot_bgcolor='#e2f0fe',
        paper_bgcolor='#e2f0fe',
        bargap=0.2,
        #width=800, 
        height=150,  
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False, 
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=True, title=None, tickfont=dict(size=14,color='#7b9cc2')), 
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=None, range=[0, max_value]),
        font=dict(size=14,color='#7b9cc2')
    )

    
    ##################
    #   Napi jegyek
    ##################


    fig_bar_days = go.Figure()

    df_fig_bar_days = df_cy_days

    # Dataframe amiben a hónapok és 0-s értékek vannak, majd ezeket a 0-kat fogjuk feltölteni értékekkel
    df_months = pd.DataFrame({
        'month': ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
        radio_value: [0,0, 0, 0, 0, 0, 0, 0, 0]
    }) 

    #átalakítjuk a create_time mezőt datetime típusuvá
    df_fig_bar_days['create_time'] = pd.to_datetime(df_fig_bar_days['create_time'])

    #kivesszük a create_time-ból a hónapok neveit
    df_fig_bar_days['month'] = df_fig_bar_days['create_time'].dt.strftime('%b') 



    #Prev year az összehasonlításos tooltip-hez ezek az adatok is kellenek
    df_py_fig_bar_days = df_py_daysprior_days

    #átalakítjuk a create_time mezőt datetime típusuvá
    df_py_fig_bar_days['create_time'] = pd.to_datetime(df_py_fig_bar_days['create_time'])

    #kivesszük a create_time-ból a hónapok neveit
    df_py_fig_bar_days['month'] = df_py_fig_bar_days['create_time'].dt.strftime('%b') 


    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        monthly_net_days = df_fig_bar_days.groupby(['month'])[radio_value].sum().reset_index()

        #elöző kiválasztott év
        monthly_net_py_days = df_py_fig_bar_days.groupby(['month'])[radio_value].sum().reset_index()

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        monthly_net_days = df_fig_bar_days.groupby(['month'])[radio_value].count().reset_index()

        #elöző kiválasztott év
        monthly_net_py_days = df_py_fig_bar_days.groupby(['month'])[radio_value].count().reset_index()


    df_monthly_net_days = pd.DataFrame({
        'month': monthly_net_days['month'],
        radio_value: monthly_net_days[radio_value]
    })


    # Mergel-jük az eredeti dataframe-t a most létrejövővel
    df_result_days = pd.merge(df_months, df_monthly_net_days, on='month', how='left')

    # A Null-os értékeket cseréljük 0-ra
    df_result_days.fillna(0, inplace=True)

    #a merge-lés miatt a radio_value_y változata kell
    df_result_days = pd.concat([df_result_days['month'], df_result_days[radio_value+'_y']], axis=1)
    df_result_days.columns = ['month', radio_value]



    df_py_monthly_net_days = pd.DataFrame({
        'month': monthly_net['month'],
        radio_value: monthly_net_py_days[radio_value]
    })

    # Mergel-jük az eredeti dataframe-t a most létrejövővel
    df_py_result_days = pd.merge(df_months, df_py_monthly_net_days, on='month', how='left')

    # A Null-os értékeket cseréljük 0-ra
    df_py_result_days.fillna(0, inplace=True)

    #a merge-lés miatt a radio_value_y változata kell
    df_py_result_days = pd.concat([df_py_result_days['month'], df_py_result_days[radio_value+'_y']], axis=1)
    df_py_result_days.columns = ['month', radio_value]


    #A megjelenítéshez kellő margin helyett, ennyi helyet hagyjon 
    max_value = df_result_days[radio_value].max() * 2
    y_axis_range = [0, max_value * 1.1] 

    # Létrehozzuk az oszlopdiagrammot, a text az oszlopok feletti szöveg lesz, aminél van plusz formázás, hogyha milliós a szám vagy hogyha nem az, illetve van egy hovertemplate, 
    # #aminél megjelenik a korábbi választott és és a választott év összegei
    fig_bar_days = go.Figure(go.Bar(
        x=df_result_days['month'],
        y=df_result_days[radio_value],
        marker_color='#aa55ff',
        text=[f"{value:.2f}" if value/1000000 < 1 else f"{value/1000000:,.2f} M" for value in df_result_days[radio_value]],
        textposition='outside',
        textangle=0,
        name='',
        hovertemplate='<b>%{x}</b><br>' + 
        f'{year_selected}: %{{y:,.0f}} {unit}<br>' +
        f'{prev_year}: %{{customdata[0]:,.0f}} {unit}',
        customdata=[[df_py_result_days[radio_value][i]] for i in range(len(df_py_result_days))]
    ))

    #Megadjuk a dizájn elemeket
    fig_bar_days.update_layout(
        xaxis_title='Month',
        yaxis_title=selected_label,
        plot_bgcolor='#eadafe',
        paper_bgcolor='#eadafe',
        bargap=0.2,
        #width=800, 
        height=150,  
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False, 
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=True, title=None, tickfont=dict(size=14,color='#ba8ab1')), 
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=None, range=y_axis_range),
        font=dict(size=14,color='#ba8ab1')
    )


    ##################
    #    Bérletek
    ##################

    fig_bar_pass = go.Figure()

    df_fig_bar_pass = df_cy_pass

    # Dataframe amiben a hónapok és 0-s értékek vannak, majd ezeket a 0-kat fogjuk feltölteni értékekkel
    df_months_pass = pd.DataFrame({
        'month': ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
        radio_value: [0,0, 0, 0, 0, 0, 0, 0, 0]
    })

    #átalakítjuk a create_time mezőt datetime típusuvá
    df_fig_bar_pass['create_time'] = pd.to_datetime(df_fig_bar_pass['create_time'])

    #kivesszük a create_time-ból a hónapok neveit
    df_fig_bar_pass['month'] = df_fig_bar_pass['create_time'].dt.strftime('%b')  



    #Prev year az összehasonlításos tooltip-hez ezek az adatok is kellenek
    df_py_fig_bar_pass = df_py_daysprior_pass

    #átalakítjuk a create_time mezőt datetime típusuvá
    df_py_fig_bar_pass['create_time'] = pd.to_datetime(df_py_fig_bar_pass['create_time'])

    #kivesszük a create_time-ból a hónapok neveit
    df_py_fig_bar_pass['month'] = df_py_fig_bar_pass['create_time'].dt.strftime('%b') 



    #A nettónál, bruttónál és a látógatószámnál ugyanúgy számolunk, sum-ot kell használnunk
    if radio_value == 'net_amount_huf' or radio_value == 'gross_amount_huf' or radio_value == 'attendance':
        monthly_net_pass = df_fig_bar_pass.groupby(['month'])[radio_value].sum().reset_index()

        #elöző kiválasztott év
        monthly_net_py_pass = df_py_fig_bar_pass.groupby(['month'])[radio_value].sum().reset_index()

    #A darabszámnál viszont count-ot kell használnunk
    elif radio_value == 'transaction_id':
        monthly_net_pass = df_fig_bar_pass.groupby(['month'])[radio_value].count().reset_index()

        #elöző kiválasztott év
        monthly_net_py_pass = df_py_fig_bar_pass.groupby(['month'])[radio_value].count().reset_index()


    df_monthly_net_pass = pd.DataFrame({
        'month': monthly_net_pass['month'],
        radio_value: monthly_net_pass[radio_value]
    })


    # Mergel-jük az eredeti dataframe-t a most létrejövővel
    df_result_pass = pd.merge(df_months_pass, df_monthly_net_pass, on='month', how='left')

    # A Null-os értékeket cseréljük 0-ra
    df_result_pass.fillna(0, inplace=True)

    #a merge-lés miatt a radio_value_y változata kell
    df_result_pass = pd.concat([df_result_pass['month'], df_result_pass[radio_value+'_y']], axis=1)
    df_result_pass.columns = ['month', radio_value]

    df_py_monthly_net_days = pd.DataFrame({
        'month': monthly_net['month'],
        radio_value: monthly_net_py_pass[radio_value]
    })

    # Mergel-jük az eredeti dataframe-t a most létrejövővel
    df_py_result_pass = pd.merge(df_months, monthly_net_py_pass, on='month', how='left')

    # A Null-os értékeket cseréljük 0-ra
    df_py_result_pass.fillna(0, inplace=True)

    #a merge-lés miatt a radio_value_y változata kell
    df_py_result_pass = pd.concat([df_py_result_pass['month'], df_py_result_pass[radio_value+'_y']], axis=1)
    df_py_result_pass.columns = ['month', radio_value]


    #A megjelenítéshez kellő margin helyett, ennyi helyet hagyjon 
    max_value = df_result_pass[radio_value].max() * 2
    y_axis_range = [0, max_value * 1.1] 

    # Létrehozzuk az oszlopdiagrammot, a text az oszlopok feletti szöveg lesz, aminél van plusz formázás, hogyha milliós a szám vagy hogyha nem az, illetve van egy hovertemplate, 
    # #aminél megjelenik a korábbi választott és és a választott év összegei
    fig_bar_pass = go.Figure(go.Bar(
        x=df_result_pass['month'],
        y=df_result_pass[radio_value],
        marker_color='#f7a47b',
        text=[f"{value:.2f}" if value/1000000 < 1 else f"{value/1000000:,.2f} M" for value in df_result_pass[radio_value]],
        textposition='outside',
        textangle=0,
        name='',
        hovertemplate='<b>%{x}</b><br>' + 
        f'{year_selected}: %{{y:,.0f}} {unit}<br>' +
        f'{prev_year}: %{{customdata[0]:,.0f}} {unit}',
        customdata=[[df_py_result_pass[radio_value][i]] for i in range(len(df_py_result_pass))]
    ))

    #Megadjuk a dizájn elemeket
    fig_bar_pass.update_layout(
        xaxis_title='Month',
        yaxis_title=selected_label,
        plot_bgcolor='#f8e9e2',
        paper_bgcolor='#f8e9e2',
        bargap=0.2,
        #width=800, 
        height=150,  
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False, 
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=True, title=None, tickfont=dict(size=14,color='#f3ae6d')), 
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=None, range=y_axis_range),
        font=dict(size=14,color='#f3ae6d')
    )

    return [filtered_kpi, filtered_days_kpi, filtered_pass_kpi, fig_line, fig_line_days, fig_line_pass, fig_bar, fig_bar_pass, fig_bar_days,None, fig_bullet, fig_bullet_days, fig_bullet_pass]
    


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
