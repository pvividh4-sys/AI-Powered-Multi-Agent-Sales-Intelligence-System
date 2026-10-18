import os
import pandas as pd

from workflow.graph import run_workflow
from reporting.word_report_generator import build_word_report


DATASET_PATH = "data/sample/Retail Sales Dataset.csv"


def main():

    print("=" * 70)
    print("WORD REPORT GENERATOR TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Load dataset
    # ---------------------------------------------------------

    print("\n[1] Loading dataset...")

    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset shape: {df.shape}")
    print(f"Dataset columns: {len(df.columns)}")

    # ---------------------------------------------------------
    # 2. Run complete 8-agent workflow
    # ---------------------------------------------------------

    print("\n[2] Running complete workflow...")

    state = run_workflow(df)

    print(
        f"Workflow status: {state.workflow_status}"
    )

    print(
        f"Current stage: {state.current_stage}"
    )

    if state.errors:

        print("\nWorkflow Errors:")

        for error in state.errors:
            print(f"- {error}")

        raise RuntimeError(
            "Workflow failed. Word report was not generated."
        )

    # ---------------------------------------------------------
    # 3. Verify Report Agent
    # ---------------------------------------------------------

    print("\n[3] Checking Report Agent...")

    report_result = state.report_result

    if not report_result:

        raise RuntimeError(
            "Report Agent result is empty."
        )

    print(
        f"Report Agent status: "
        f"{report_result.get('status')}"
    )

    print(
        f"Report validation: "
        f"{report_result.get('report_validation')}"
    )

    print(
        f"Report sections: "
        f"{report_result.get('total_sections')}"
    )

    # ---------------------------------------------------------
    # 4. Extract actual report
    # ---------------------------------------------------------

    report = report_result.get("report")

    if not report:

        raise RuntimeError(
            "Report Agent did not return a report object."
        )

    # ---------------------------------------------------------
    # 5. Generate Word document
    # ---------------------------------------------------------

    print("\n[4] Generating Word report...")

    output_path = build_word_report(
        report=report,
        output_directory="reports",
        filename="Sales_Intelligence_Report.docx",
        dataset_name=os.path.basename(DATASET_PATH),
    )

    # ---------------------------------------------------------
    # 6. Verify file
    # ---------------------------------------------------------

    print("\n[5] Verifying generated file...")

    if not os.path.isfile(output_path):

        raise RuntimeError(
            "Word report file was not created."
        )

    file_size = os.path.getsize(output_path)

    print(
        f"Output file: {output_path}"
    )

    print(
        f"File size: {file_size:,} bytes"
    )

    if file_size == 0:

        raise RuntimeError(
            "Generated Word report is empty."
        )

    # ---------------------------------------------------------
    # 7. Final result
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("WORD REPORT TEST: PASSED")
    print("=" * 70)

    print(
        f"\nGenerated successfully:\n"
        f"{output_path}"
    )


if __name__ == "__main__":
    main()