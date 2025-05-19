# Import necessary libraries and modules
import pytest
import pandas as pd
from Sales_analysis_app import (
    TrendsOverTime,
    LocationDistribution,
    PairProductAnalysis,
    BestSellingProductAnalysis,
    ProductPerformanceAnalysis
)

DATASET_PATH = "Sales_Data.xlsx"

# Define a pytest fixture to load the dataset
@pytest.fixture(scope="module")
def load_data():
    """Load test dataset."""
    try:
        data = pd.read_excel(DATASET_PATH)
        data.columns = data.columns.str.strip()  
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")  
        return data
    except Exception as e:
        pytest.fail(f"Failed to load dataset: {e}")

# Test: Trends Over Time
def test_trends_over_time(load_data):
    trends = TrendsOverTime()
    result = trends.process_data(load_data)

    # Assertions
    assert "Date" in result.columns, "Missing 'Date' column in TrendsOverTime output"
    assert "TotalTransactions" in result.columns, "Missing 'TotalTransactions' column in TrendsOverTime output"
    assert not result.empty, "TrendsOverTime returned an empty output"
    assert (result["TotalTransactions"] >= 0).all(), "Invalid transaction count in TrendsOverTime"

# Test: Regional Analysis
def test_location_distribution(load_data):
    location_analysis = LocationDistribution()
    result = location_analysis.process_data(load_data)

    # Assertions
    assert "Location" in result.columns, "Missing 'Location' column in LocationDistribution output"
    assert "CustomerCount" in result.columns, "Missing 'CustomerCount' column in LocationDistribution output"
    assert not result.empty, "LocationDistribution returned an empty output"
    assert (result["CustomerCount"] >= 0).all(), "Invalid customer count in LocationDistribution"

# Test: Pair Product Analysis
def test_pair_product_analysis(load_data):
    pair_analysis = PairProductAnalysis()
    result = pair_analysis.process_data(load_data)

    # Assertions
    assert "Product 1" in result.columns, "Missing 'Product 1' column in PairProductAnalysis output"
    assert "Product 2" in result.columns, "Missing 'Product 2' column in PairProductAnalysis output"
    assert "Frequency" in result.columns, "Missing 'Frequency' column in PairProductAnalysis output"
    assert not result.empty, "PairProductAnalysis returned an empty output"
    assert (result["Frequency"] >= 0).all(), "Invalid frequency in PairProductAnalysis"

# Test: Best-Selling Products
def test_best_selling_products(load_data):
    best_selling = BestSellingProductAnalysis()
    result = best_selling.process_data(load_data)

    # Assertions
    assert "Purchase Category" in result.columns, "Missing 'Purchase Category' column in BestSellingProductAnalysis output"
    assert "Frequency" in result.columns, "Missing 'Frequency' column in BestSellingProductAnalysis output"
    assert not result.empty, "BestSellingProductAnalysis returned an empty output"
    assert result["Frequency"].max() > 0, "No valid best-selling products found"

# Test: Product Performance
def test_product_performance(load_data):
    performance = ProductPerformanceAnalysis()
    result = performance.process_data(load_data)

    # Assertions
    assert "Month" in result.columns, "Missing 'Month' column in ProductPerformanceAnalysis output"
    assert "Product Category" in result.columns, "Missing 'Product Category' column in ProductPerformanceAnalysis output"
    assert "Sales" in result.columns, "Missing 'Sales' column in ProductPerformanceAnalysis output"
    assert not result.empty, "ProductPerformanceAnalysis returned an empty output"
    assert (result["Sales"] >= 0).all(), "Invalid sales data in ProductPerformanceAnalysis"

# Edge Case: Empty Dataset
def test_empty_dataset():
    empty_data = pd.DataFrame()

    # Assertions for each analysis class
    assert TrendsOverTime().process_data(empty_data).empty, "TrendsOverTime failed with empty dataset"
    assert LocationDistribution().process_data(empty_data).empty, "LocationDistribution failed with empty dataset"
    assert PairProductAnalysis().process_data(empty_data).empty, "PairProductAnalysis failed with empty dataset"
    assert BestSellingProductAnalysis().process_data(empty_data).empty, "BestSellingProductAnalysis failed with empty dataset"
    assert ProductPerformanceAnalysis().process_data(empty_data).empty, "ProductPerformanceAnalysis failed with empty dataset"

# Performance Test: Large Dataset
def test_large_dataset():
    large_data = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=100000, freq="H"),
        "Customer_ID": [i % 1000 for i in range(100000)],
        "Purchase Category": ["Category " + str(i % 10) for i in range(100000)],
        "Location": ["Location " + str(i % 5) for i in range(100000)],
    })

    # Assertions for each analysis class
    assert not TrendsOverTime().process_data(large_data).empty, "TrendsOverTime failed with large dataset"
    assert not LocationDistribution().process_data(large_data).empty, "LocationDistribution failed with large dataset"
    assert not PairProductAnalysis().process_data(large_data).empty, "PairProductAnalysis failed with large dataset"
    assert not BestSellingProductAnalysis().process_data(large_data).empty, "BestSellingProductAnalysis failed with large dataset"
    assert not ProductPerformanceAnalysis().process_data(large_data).empty, "ProductPerformanceAnalysis failed with large dataset"


