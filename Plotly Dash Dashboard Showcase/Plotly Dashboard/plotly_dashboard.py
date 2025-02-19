import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly_express as px
import plotly.graph_objects as go
import pandas as pd

mapboxToken = "pk.eyJ1IjoiMTcyOTQ0bCIsImEiOiJjazMzdjY3YmMwcW5qM2dxaXl6bmI0N3NtIn0.921tzGi6WiSVeyAtyqM6xQ"

year = [2015,2016,2017,2018]
superstore_df = pd.read_excel('Superstore Sample.xlsx')
telecom_df = pd.read_csv('Orange Telecom Churn Data Updated.csv')
townDataset = pd.read_excel('Town.xlsx')

combinedTable = pd.merge(left=telecom_df, right=townDataset, left_on='Region', right_on="Town")
combinedTableChurnedOnly = combinedTable[combinedTable['churned'] == True]

combinedTableChurnedOnly['Churn_Date'] = pd.to_datetime(combinedTableChurnedOnly.Churn_Date)

superstore_df['Profit_Ratio'] = ""

for ind,row in superstore_df.iterrows():
    profitRatio = (row.Profit / row.Sales)*100
    superstore_df['Profit_Ratio'].iloc[ind] = profitRatio

superstore_df['Profit_Ratio'] = superstore_df.Profit_Ratio.astype(float)

superstore_renamed_df = superstore_df.rename(columns={"Customer ID":"Customer_ID","Customer Name":"Customer_Name"})
sortedSales_df = superstore_renamed_df.groupby(['Customer_ID','Customer_Name'], axis=0).sum().reset_index().sort_values('Sales',ascending=False)

figMap = px.scatter_mapbox(
    combinedTableChurnedOnly,
    lat=combinedTableChurnedOnly.Latitude.unique(),
    lon=combinedTableChurnedOnly.Longitude.unique(),
    hover_name=combinedTableChurnedOnly.Region.unique(),
    size=combinedTableChurnedOnly.groupby('Region')['Region'].count().tolist(),
    color=combinedTableChurnedOnly.groupby('Region')['Region'].count().tolist(),
    color_continuous_scale=px.colors.cyclical.IceFire,
    #color_discrete_sequence=["fuchsia"],
    zoom=9.7,
    height=500,
)

figMap.update_layout(mapbox_style="light", mapbox_accesstoken=mapboxToken)
figMap.update_layout(margin={"r":0,"t":40,"l":0,"b":10})
figMap.update_layout(title="No of Churns per Region")

saleScatterplot = px.scatter(
    superstore_df,
    x="Sales",
    y="Profit",
    color="Profit_Ratio",
    color_continuous_scale= "Portland"
)
saleScatterplot.update_layout(
    title="Sales and Profit by Customer",
    xaxis_title="Sales($)",
    yaxis_title="Profit($)"
)

totalSalesBar = px.bar(
    x=sortedSales_df.Customer_Name,
    y=sortedSales_df.Sales
)
totalSalesBar.update_layout(
    title="Customer Rank",
    yaxis_title="Sales($)",
    xaxis_title="Customer Name",
    xaxis=go.layout.XAxis(
        rangeslider=dict(visible=True)
    )
)

figPieChartChurn = go.Figure(
    data=[go.Pie(
        labels=telecom_df.churned.unique(),
        values=telecom_df.groupby('churned')['churned'].count().tolist(),
        hole=.5,
        title="Churn Percentage")
])
figPieChartChurn.update_layout(title="Percentage of Customers Churn")

figPieChartIntlPlan = go.Figure(
    data=[go.Pie(
        labels=telecom_df.intl_plan.unique(),
        values=telecom_df.groupby('intl_plan')['intl_plan'].count().tolist(),
        title="International Plan Subscription",
        hole=.5)
])
figPieChartIntlPlan.update_layout(title="Percentage of International Plan")

#churnDateLine = px.line(
#    combinedTableChurnedOnly,
#    x=combinedTableChurnedOnly.Churn_Date.dt.year.unique().tolist(),
#    y=combinedTableChurnedOnly.groupby(combinedTableChurnedOnly.Churn_Date.dt.year).count().tolist()
#)



app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Tabs(id="tabs", children=[

        dcc.Tab(label='Superstore Dataset', children=[
            html.H1("Superstore Analysis"),
            html.Div([
                dcc.Graph(figure=saleScatterplot),

            ]),

            html.Div([
                dcc.Graph(figure=totalSalesBar)
            ],
                style={
                'overflowX': 'scroll'
            }),

        ]),

        dcc.Tab(label='Telecom Churn Dataset', children=[
            html.H1("Telecom Analysis"),
            html.Div([
                dcc.Graph(figure=figPieChartChurn),
                #dcc.Graph(figure=churnDateLine),
                dcc.Graph(figure=figMap),
                #dcc.Graph(figure=figPieChartIntlPlan)
            ])
        ])
    ])
])


app.run_server(debug=True)
