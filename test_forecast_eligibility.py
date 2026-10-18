import os
import sys

import pandas as pd


# Allow imports from the project root
sys.path.insert(
    0,
    os.path.dirname(os.path.abspath(__file__))
)

from forecasting.eligibility import (
    check_forecast_eligibility,
    is_forecast_eligible,
)


DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data",
    "sample",
    "Retail Sales Dataset.csv",
)


def main():

    print("=" * 70)
    print("8.6.1 FORECAST ELIGIBILITY TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # Load dataset
    # ---------------------------------------------------------

    print("\n1. Loading dataset...")

    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset Shape: {df.shape}")

    # ---------------------------------------------------------
    # Planner semantic mapping
    # ---------------------------------------------------------

    semantic_mapping = {
        "date": "Date",
        "sales": "Total Amount",
        "quantity": "Quantity",
        "product": "Product Category",
        "customer": "Customer ID",
        "region": "City",
        "order_id": "Order ID",
    }

    print("\n2. Semantic Mapping")
    print(f"Date Column : {semantic_mapping['date']}")
    print(f"Sales Column: {semantic_mapping['sales']}")

    # ---------------------------------------------------------
    # Run eligibility
    # ---------------------------------------------------------

    print("\n3. Running Forecast Eligibility...")

    result = check_forecast_eligibility(
        df=df,
        semantic_mapping=semantic_mapping,
    )

    # ---------------------------------------------------------
    # Display result
    # ---------------------------------------------------------

    print("\n" + "-" * 70)
    print("FORECAST ELIGIBILITY RESULT")
    print("-" * 70)

    print(f"Eligible           : {result.eligible}")
    print(f"Date Column        : {result.date_column}")
    print(f"Sales Column       : {result.sales_column}")
    print(f"Valid Observations : {result.observations}")
    print(f"Unique Dates       : {result.unique_dates}")
    print(f"Start Date         : {result.start_date}")
    print(f"End Date           : {result.end_date}")
    print(f"Frequency          : {result.frequency}")

    print("\nValidation Checks")
    print("-" * 70)

    print(f"Date Valid         : {result.date_valid}")
    print(f"Sales Valid        : {result.sales_valid}")
    print(f"Sufficient History: {result.sufficient_history}")
    print(f"Consistent Series  : {result.consistent_series}")
    print(f"Acceptable Quality : {result.acceptable_quality}")

    print("\nReasons")
    print("-" * 70)

    for reason in result.reasons:
        print(f"- {reason}")

    # ---------------------------------------------------------
    # Convenience function
    # ---------------------------------------------------------

    simple_result = is_forecast_eligible(
        df=df,
        semantic_mapping=semantic_mapping,
    )

    print("\nSimple Eligibility Check")
    print("-" * 70)
    print(f"is_forecast_eligible(): {simple_result}")

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert result.date_column == "Date"

    assert result.sales_column == "Total Amount"

    assert result.date_valid is True

    assert result.sales_valid is True

    assert result.observations > 0

    assert result.unique_dates > 0

    assert result.start_date == "2023-01-01"

    assert result.end_date == "2024-01-01"

    assert result.frequency in {"D", "W", "M"}

    assert result.sufficient_history is True

    assert result.acceptable_quality is True

    assert result.eligible is True

    assert simple_result is True

    print("\n" + "=" * 70)
    print("8.6.1 FORECAST ELIGIBILITY TEST: PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()