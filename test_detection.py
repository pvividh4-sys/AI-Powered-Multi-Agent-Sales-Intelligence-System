import pandas as pd

from agents.planner_agent import PlannerAgent
from cleaning.detection import DataQualityDetector


def main():

    print("\n")
    print("=" * 50)
    print("       DATA QUALITY DETECTION TEST")
    print("=" * 50)

    # =========================================================
    # LOAD DATASET
    # =========================================================

    file_path = "data/sample/Retail Sales Dataset.csv"

    df = pd.read_csv(file_path)

    print("\nDATASET")
    print("-" * 50)
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # =========================================================
    # RUN PLANNER
    # =========================================================

    print("\nRUNNING PLANNER")
    print("-" * 50)

    planner = PlannerAgent()

    planner_result = planner.run(df)

    # ---------------------------------------------------------
    # Check Planner status
    # ---------------------------------------------------------

    print(
        f"Planner Status: "
        f"{planner_result.get('status', 'unknown')}"
    )

    # =========================================================
    # GET SEMANTIC MAPPING
    # =========================================================

    semantic_mapping = planner_result.get(
        "semantic_mapping",
        {}
    )

    print("\nSEMANTIC MAPPING")
    print("-" * 50)

    if not semantic_mapping:

        print("No semantic mapping returned by Planner.")

    else:

        for role, value in semantic_mapping.items():

            if isinstance(value, dict):

                column = value.get(
                    "column",
                    "N/A"
                )

                confidence = value.get(
                    "confidence",
                    "N/A"
                )

                print(
                    f"{role}: {column} "
                    f"| confidence: {confidence}"
                )

            else:

                print(
                    f"{role}: {value}"
                )

    # =========================================================
    # RUN DATA QUALITY DETECTOR
    # =========================================================

    print("\nRUNNING DATA QUALITY DETECTOR")
    print("-" * 50)

    detector = DataQualityDetector(
        df=df,
        semantic_mapping=semantic_mapping
    )

    # ---------------------------------------------------------
    # Basic quality
    # ---------------------------------------------------------

    quality = detector.detect_basic_quality()

    # ---------------------------------------------------------
    # Detect all issues
    # ---------------------------------------------------------

    issues = detector.detect_all()

    # =========================================================
    # DATASET QUALITY
    # =========================================================

    print("\nDATASET QUALITY")
    print("-" * 50)

    print(
        f"Rows: {quality['rows']}"
    )

    print(
        f"Columns: {quality['columns']}"
    )

    print(
        f"Missing values: "
        f"{quality['missing_values']}"
    )

    print(
        f"Duplicate rows: "
        f"{quality['duplicate_rows']}"
    )

    # =========================================================
    # NUMERIC BUSINESS COLUMNS
    # =========================================================

    numeric_columns = (
        detector.get_numeric_business_columns()
    )

    print("\nNUMERIC BUSINESS COLUMNS")
    print("-" * 50)

    if numeric_columns:

        for column in numeric_columns:
            print(f"- {column}")

    else:

        print("No numeric business columns detected.")

    # =========================================================
    # TOTAL ISSUES
    # =========================================================

    print("\nTOTAL ISSUES")
    print("-" * 50)

    print(len(issues))

    # =========================================================
    # DETECTED ISSUES
    # =========================================================

    print("\nDETECTED ISSUES")
    print("-" * 50)

    if not issues:

        print("No data-quality issues detected.")

    else:

        for issue in issues:

            print("\n" + "-" * 50)

            print(
                f"Issue ID: "
                f"{issue['issue_id']}"
            )

            print(
                f"Issue Type: "
                f"{issue['issue_type']}"
            )

            print(
                f"Column: "
                f"{issue['column']}"
            )

            print(
                f"Affected Rows: "
                f"{issue['affected_rows']}"
            )

            print(
                f"Risk Level: "
                f"{issue['risk_level']}"
            )

            print(
                f"Approval Required: "
                f"{issue['requires_approval']}"
            )

            print(
                f"Evidence: "
                f"{issue['evidence']}"
            )

            # -------------------------------------------------
            # Invalid examples
            # -------------------------------------------------

            if "invalid_examples" in issue:

                print(
                    f"Invalid Examples: "
                    f"{issue['invalid_examples']}"
                )

            # -------------------------------------------------
            # Median
            # -------------------------------------------------

            if "computed_median" in issue:

                print(
                    f"Computed Median: "
                    f"{issue['computed_median']}"
                )

            # -------------------------------------------------
            # Parsing strategy
            # -------------------------------------------------

            if "parsing_strategy" in issue:

                print(
                    f"Parsing Strategy: "
                    f"{issue['parsing_strategy']}"
                )

            # -------------------------------------------------
            # Outlier boundaries
            # -------------------------------------------------

            if "lower_bound" in issue:

                print(
                    f"Lower Bound: "
                    f"{issue['lower_bound']}"
                )

            if "upper_bound" in issue:

                print(
                    f"Upper Bound: "
                    f"{issue['upper_bound']}"
                )

            # -------------------------------------------------
            # Warning
            # -------------------------------------------------

            if "warning" in issue:

                print(
                    f"Warning: "
                    f"{issue['warning']}"
                )

    # =========================================================
    # ISSUE SUMMARY
    # =========================================================

    print("\n")
    print("=" * 50)
    print("       ISSUE SUMMARY")
    print("=" * 50)

    issue_types = {}

    for issue in issues:

        issue_type = issue["issue_type"]

        issue_types[issue_type] = (
            issue_types.get(issue_type, 0) + 1
        )

    if issue_types:

        for issue_type, count in issue_types.items():

            print(
                f"{issue_type}: {count}"
            )

    else:

        print("No issues detected.")

    # =========================================================
    # FINAL STATUS
    # =========================================================

    print("\n")
    print("=" * 50)
    print("       DETECTION TEST COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()