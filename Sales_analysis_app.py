# Import required libraries
import pandas as pd  
from abc import ABC, abstractmethod  
import dash  
from dash import html, dcc  
from dash.dependencies import Input, Output  
import plotly.express as px  
from itertools import combinations  
from collections import Counter  

# Define the abstract interface for data ingestion
class DataIngestionStrategy(ABC):
    @abstractmethod
    def ingest_data(self, file_path):
        pass  

# Define the concrete implementation for Excel data ingestion
class ExcelDataIngestion(DataIngestionStrategy):
    def ingest_data(self, file_path):
        try:
            data = pd.read_excel(file_path)  # Read Excel file
            # Strip whitespace from column names to avoid issues during processing
            data.columns = data.columns.str.strip()
            return data
        except Exception as e:
            print(f"Error loading Excel file: {e}")  # Log errors for debugging
            return pd.DataFrame()  # Return an empty DataFrame if file cannot be loaded

# Define a context class to dynamically switch data ingestion strategies
class DataIngestionContext:
    def __init__(self, strategy: DataIngestionStrategy):
        self._strategy = strategy 

    def set_strategy(self, strategy: DataIngestionStrategy):
        self._strategy = strategy  

    def ingest(self, file_path):
        return self._strategy.ingest_data(file_path)  

# Define an abstract interface for data processing
class DataProcess(ABC):
    @abstractmethod
    def process_data(self, data):
        pass  

# Define a class for analyzing trends over time
class TrendsOverTime(DataProcess):
    def process_data(self, data):
        # Validate required columns
        if 'Date' not in data.columns or 'Customer_ID' not in data.columns:
            print("Warning: Required columns for Trends Over Time are missing.")
            return pd.DataFrame(columns=['Date', 'TotalTransactions'])  # Return an empty DataFrame if columns are missing
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')  # Convert Date column to datetime
        grouped = data.groupby(data['Date'].dt.to_period("M"))['Customer_ID'].count().reset_index()  # Group by month
        grouped.columns = ['Date', 'TotalTransactions']  # Rename columns
        grouped['Date'] = grouped['Date'].dt.to_timestamp()  # Convert period to timestamp
        return grouped

# Define a class for analyzing sales distribution by location
class LocationDistribution(DataProcess):
    def process_data(self, data):
        # Validate required columns
        if 'Location' not in data.columns or 'Customer_ID' not in data.columns:
            print("Warning: Required columns for Location Distribution are missing.")
            return pd.DataFrame(columns=['Location', 'CustomerCount'])  # Return an empty DataFrame if columns are missing
        return data.groupby('Location')['Customer_ID'].count().reset_index(name='CustomerCount').sort_values(by='CustomerCount', ascending=False)

# Define a class for analyzing frequently purchased product pairs
class PairProductAnalysis(DataProcess):
    def process_data(self, data):
        # Validate required columns
        if 'Customer_ID' not in data.columns or 'Purchase Category' not in data.columns:
            print("Warning: Required columns for Pair Product Analysis are missing.")
            return pd.DataFrame(columns=['Product 1', 'Product 2', 'Frequency'])  # Return an empty DataFrame if columns are missing
        grouped_data = data.groupby('Customer_ID')['Purchase Category'].apply(list)  # Group product categories by customer
        pairs = []
        for items in grouped_data:
            pairs.extend(combinations(items, 2))  # Generate all possible pairs of products
        pair_counts = Counter(pairs)  # Count the occurrences of each pair
        pair_df = pd.DataFrame(pair_counts.items(), columns=['Pair', 'Frequency'])  # Convert counts to DataFrame
        pair_df['Product 1'], pair_df['Product 2'] = zip(*pair_df['Pair'])  # Split pairs into separate columns
        return pair_df.drop(columns=['Pair']).sort_values(by='Frequency', ascending=False)

# Define a class for analyzing best-selling products
class BestSellingProductAnalysis(DataProcess):
    def process_data(self, data):
        # Validate required columns
        if 'Purchase Category' not in data.columns or 'Customer_ID' not in data.columns:
            print("Warning: Required columns for Best Selling Product Analysis are missing.")
            return pd.DataFrame(columns=['Purchase Category', 'Frequency'])  # Return an empty DataFrame if columns are missing
        top_categories = data.groupby('Purchase Category')['Customer_ID'].count().reset_index(name='Frequency')  # Count transactions per category
        return top_categories.sort_values(by='Frequency', ascending=False).head(10)  # Return the top 10 categories

# Define a class for analyzing product performance over time
class ProductPerformanceAnalysis(DataProcess):
    def process_data(self, data):
        # Validate required columns
        if 'Date' not in data.columns or 'Purchase Category' not in data.columns or 'Customer_ID' not in data.columns:
            print("Warning: Required columns for Product Performance Analysis are missing.")
            return pd.DataFrame(columns=['Month', 'Product Category', 'Sales'])  # Return an empty DataFrame if columns are missing
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')  # Convert Date column to datetime
        trends = data.groupby([data['Date'].dt.to_period("M"), 'Purchase Category'])['Customer_ID'].count().reset_index()  # Group by month and category
        trends.columns = ['Month', 'Product Category', 'Sales']  # Rename columns
        trends['Month'] = trends['Month'].dt.to_timestamp()  # Convert period to timestamp
        return trends

# File path to the dataset
file_path = r"Sales_Data.xlsx"  

# Initialize the data ingestion context and ingest data
data_ingestion_context = DataIngestionContext(ExcelDataIngestion())  # Use Excel ingestion strategy
sales_data = data_ingestion_context.ingest(file_path)  # Load sales data

# Initialize the Dash application
app = dash.Dash(__name__)

# Define the layout of the application
app.layout = html.Div(
    children=[
        html.H1(
            children='Customer Sales Analysis',  # Title of the application
            style={'textAlign': 'center', 'color': '#2C3E50', 'padding': '20px'},
        ),
        # Dropdowns for Year and Month selection
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3('Select Year:', style={'color': '#2C3E50'}),
                        dcc.Dropdown(
                            id='year-dropdown',
                            options=[{'label': str(year), 'value': year} for year in sorted(sales_data['Date'].dt.year.unique())],
                            placeholder='Select Year',
                        ),
                    ],
                    style={'width': '48%', 'display': 'inline-block'},
                ),
                html.Div(
                    children=[
                        html.H3('Select Month:', style={'color': '#2C3E50'}),
                        dcc.Dropdown(id='month-dropdown', placeholder='Select Month'),
                    ],
                    style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'},
                ),
            ],
        ),
        # Dropdown for selecting chart type
        html.H3(
            'Select a Chart to Display:', style={'color': '#2C3E50', 'paddingTop': '20px'}
        ),
        dcc.Dropdown(
            id='chart-selector',
            options=[
                {'label': 'Trends Over Time', 'value': 'trends-over-time'},
                {'label': 'Regional Sales Analysis', 'value': 'location-distribution'},
                {'label': 'Pair Product Analysis', 'value': 'pair-product-analysis'},
                {'label': 'Best-Selling Products', 'value': 'best-selling-products'},
                {'label': 'Product Performance', 'value': 'product-performance'},
            ],
            value='trends-over-time',
        ),
        # Placeholder for dynamic chart
        html.Div(id='dynamic-chart'),
    ],
    style={'backgroundColor': '#ECF0F1', 'padding': '30px'},
)

# Callback for updating Month dropdown based on selected Year
@app.callback(
    Output('month-dropdown', 'options'),
    [Input('year-dropdown', 'value')],
)
def update_month_options(selected_year):
    if selected_year is None:
        return []
    months = sales_data[sales_data['Date'].dt.year == selected_year]['Date'].dt.month.unique()
    return [{'label': str(month), 'value': month} for month in sorted(months)]

# Callback for generating dynamic visualizations
@app.callback(
    Output('dynamic-chart', 'children'),
    [Input('year-dropdown', 'value'), Input('month-dropdown', 'value'), Input('chart-selector', 'value')],
)
def update_visualizations(selected_year, selected_month, selected_chart):
    filtered_data = sales_data.copy()
    if selected_year:
        filtered_data = filtered_data[filtered_data['Date'].dt.year == selected_year]
    if selected_month:
        filtered_data = filtered_data[filtered_data['Date'].dt.month == selected_month]
    if selected_chart == 'trends-over-time':
        trends_data = TrendsOverTime().process_data(filtered_data)
        fig = px.line(trends_data, x='Date', y='TotalTransactions', title='Trends Over Time')
    elif selected_chart == 'location-distribution':
        location_data = LocationDistribution().process_data(filtered_data)
        fig = px.bar(location_data, x='Location', y='CustomerCount', title='Regional Sales Analysis')
    elif selected_chart == 'pair-product-analysis':
        pair_product_data = PairProductAnalysis().process_data(filtered_data)
        fig = px.bar(
            pair_product_data.head(10), x='Product 1', y='Frequency', color='Product 2', title='Top Product Pairs Purchased Together'
        )
    elif selected_chart == 'best-selling-products':
        best_selling_products = BestSellingProductAnalysis().process_data(filtered_data)
        fig = px.bar(best_selling_products, x='Purchase Category', y='Frequency', title='Best-Selling Products')
    elif selected_chart == 'product-performance':
        product_performance = ProductPerformanceAnalysis().process_data(filtered_data)
        fig = px.line(product_performance, x='Month', y='Sales', color='Product Category', title='Product Performance Over Time')
    else:
        fig = None
    return dcc.Graph(figure=fig) if fig else None

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True)
