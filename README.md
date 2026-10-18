# AI-Powered Multi-Agent Sales Intelligence System

## 1. Project Overview

The **AI-Powered Multi-Agent Sales Intelligence System** is a domain-specific Agentic AI decision-support system designed for **Retail and E-commerce Sales Analytics**.

The system accepts a sales CSV dataset and autonomously coordinates a complete analytical workflow:

```text
Sales CSV
   ↓
Planner Agent
   ↓
Data Cleaning Agent
   ↓
EDA Agent
   ↓
Visualization Agent
   ↓
Forecasting Agent (when applicable)
   ↓
Insight Agent
   ↓
Recommendation Agent
   ↓
Report Agent
   ↓
Sales Intelligence Report
```

The system is designed to reduce the amount of manual analytical orchestration required from the user while maintaining:

- Human control over high-risk data modifications
- Deterministic numerical computation
- LLM-based reasoning where it provides value
- Validation at important stages
- Conditional agent routing
- Feedback loops
- Decision traceability
- Grounded insights and recommendations

The project is **not intended to replace a human sales analyst**. It is a research-oriented decision-support system that investigates how specialized AI agents can coordinate an end-to-end sales analytics workflow.

---

# 2. Core Design Philosophy

The central principle of the system is:

> **The system should be autonomous in orchestration and reasoning, but controlled and traceable when modifying data or making high-risk analytical decisions.**

The system therefore separates:

```text
Detection
   ↓
Reasoning
   ↓
Recommendation
   ↓
Risk Classification
   ↓
Policy Validation
   ↓
Human Approval
   ↓
Execution
   ↓
Validation
   ↓
Logging
```

This distinction is especially important for data cleaning.

The LLM is not allowed to directly modify the dataset.

Instead:

```text
Python / Statistical Tools
        ↓
Detect actual data problem
        ↓
LLM
        ↓
Reason about the detected problem
        ↓
Recommend an action
        ↓
System Policy
        ↓
Determine risk and approval requirement
        ↓
Human
        ↓
Approve / Skip / Modify
        ↓
Python
        ↓
Execute
        ↓
Python
        ↓
Validate
```

This allows the project to demonstrate meaningful Agentic AI behaviour without giving an LLM uncontrolled authority over destructive data operations.

---

# 3. Domain and Scope

## 3.1 Primary Domain

**Retail and E-commerce Sales Intelligence**

## 3.2 Sub-domain

**Sales Analytics and Business Decision Support**

## 3.3 Typical Dataset

The system is designed for transactional or periodic sales datasets containing some combination of:

```text
Order ID
Order Date
Product
Category
Customer
Region
State / City
Quantity
Sales / Revenue
Cost
Profit
Discount
```

The system does **not** require every column to exist.

For example:

```text
Order Date
Product
Sales
```

can support:

- Sales trend analysis
- Product analysis
- Forecasting, if sufficient historical observations exist

But it cannot legitimately support:

- Customer analysis
- Regional analysis
- Profitability analysis

The Planner Agent detects these limitations and routes the workflow accordingly.

---

# 4. Problem Statement

Traditional sales analysis often requires a human analyst to:

1. Inspect the dataset.
2. Understand its schema.
3. Clean the data.
4. Decide which analyses are relevant.
5. Calculate KPIs.
6. Create appropriate charts.
7. Perform forecasting where appropriate.
8. Interpret results.
9. Develop business recommendations.
10. Prepare a report.

A general-purpose LLM can perform many individual tasks, but the user generally has to provide prompts and manually coordinate the workflow.

This project investigates:

> **How can a domain-specific multi-agent architecture autonomously transform raw retail/e-commerce sales data into validated, actionable sales intelligence with minimal human intervention?**

The focus is therefore not simply on using an LLM to analyse a CSV.

The focus is on:

```text
Planning
+
Agent Routing
+
Specialized Agents
+
Tool Use
+
Conditional Execution
+
Validation
+
Feedback
+
Grounded Reasoning
+
Traceability
```

---

# 5. Project Objectives

The system aims to:

1. Automatically inspect uploaded sales data.
2. Detect dataset schema and analytical capabilities.
3. Create an analysis plan dynamically.
4. Identify and handle data-quality problems.
5. Use deterministic tools for numerical calculations.
6. Use LLM reasoning where interpretation or semantic decisions are useful.
7. Provide risk-aware cleaning recommendations.
8. Require human approval for high-risk cleaning actions.
9. Perform sales-oriented exploratory data analysis.
10. Automatically select appropriate visualizations.
11. Determine whether forecasting is applicable.
12. Select and evaluate forecasting approaches where applicable.
13. Generate grounded business insights.
14. Convert insights into evidence-based recommendations.
15. Generate a consolidated report.
16. Maintain traceability between data, decisions, analytical results, insights and recommendations.
17. Reduce manual prompting and analytical orchestration.
18. Evaluate the system using measurable technical and business-oriented metrics.

---

# 6. Eight-Agent Architecture

The project contains exactly **eight specialized agents**.

```text
1. Planner Agent
2. Data Cleaning Agent
3. EDA Agent
4. Visualization Agent
5. Forecasting Agent
6. Insight Agent
7. Recommendation Agent
8. Report Agent
```

No additional agent is required for:

- Risk management
- Approval
- Validation
- Logging

These are workflow capabilities and control layers implemented around the existing agents.

---

# 7. Overall Architecture

```text
                         USER
                           │
                           ▼
                      SALES CSV
                           │
                           ▼
                  ┌─────────────────┐
                  │  PLANNER AGENT  │
                  │                 │
                  │ Schema Analysis │
                  │ Capability      │
                  │ Detection       │
                  │ Planning        │
                  │ Routing         │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ DATA CLEANING   │
                  │     AGENT       │
                  │                 │
                  │ Issue Detection │
                  │ Classification  │
                  │ LLM Reasoning   │
                  │ Recommendations │
                  └────────┬────────┘
                           │
                           ▼
                 ┌─────────────────────┐
                 │ RISK / POLICY LAYER │
                 └──────────┬──────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
          LOW-RISK ACTION        MEDIUM/HIGH-RISK
          Policy Controlled      HUMAN REVIEW
                                      │
                              ┌───────┴───────┐
                              ▼               ▼
                           APPROVE          SKIP
                              │               │
                              └───────┬───────┘
                                      ▼
                             PYTHON EXECUTION
                                      │
                                      ▼
                                  VALIDATION
                                      │
                                      ▼
                                  EDA AGENT
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                 VISUALIZATION AGENT        FORECASTING AGENT
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                                INSIGHT AGENT
                                      │
                                      ▼
                           RECOMMENDATION AGENT
                                      │
                                      ▼
                                REPORT AGENT
                                      │
                                      ▼
                               FINAL REPORT
                                      │
                                      ▼
                                DECISION LOG
```

---

# 8. Common Agent Contract

Every agent should have a bounded responsibility.

The conceptual contract is:

```text
Input
  ↓
Preconditions
  ↓
Context / Shared State
  ↓
Bounded Decision
  ↓
Tool or Analytical Action
  ↓
Validation
  ↓
Structured Output
  ↓
Shared State
```

The system should **not** simply contain eight Python functions named "agents".

Each agent must make a bounded decision appropriate to its responsibility.

For example:

```text
EDA Agent
   ↓
Are suitable numerical variables available?
   ↓
YES → Run correlation analysis
NO  → Skip correlation analysis
```

The same principle applies throughout the system.

---

# 9. Shared Agent State

The agents communicate through a shared workflow state.

A conceptual state is:

```text
AgentState
│
├── raw_dataset
├── schema
├── detected_columns
├── semantic_mapping
├── data_quality_report
├── cleaning_plan
├── cleaning_decisions
├── cleaning_actions
├── cleaning_log
├── cleaned_dataset
├── analysis_plan
├── KPI_results
├── EDA_results
├── visualization_plan
├── charts
├── forecasting_eligibility
├── forecast_model_results
├── forecast_metrics
├── forecast_values
├── insights
├── recommendations
├── validation_results
├── decision_trace
└── final_report
```

Each agent reads the information it needs and writes structured outputs back to the shared state.

---

# 10. Agent 1 — Planner Agent

## 10.1 Purpose

The Planner Agent is the **workflow orchestration and decision-making agent**.

It determines:

- What the dataset contains
- What the dataset can support
- Which analyses are relevant
- Which agents/tasks need to execute
- Whether forecasting is possible
- What sequence or routing should be used

## 10.2 Input

```text
Raw Sales CSV
User objective, if supplied
Dataset metadata
```

## 10.3 Schema Analysis

The Planner identifies:

- Column names
- Data types
- Numeric columns
- Categorical columns
- Date/time columns
- Identifier columns
- Potential sales/revenue columns
- Potential profit columns
- Product columns
- Customer columns
- Geographic columns
- Quantity columns
- Discount columns

Example:

```text
Detected:

Date       → Order Date
Sales      → Revenue
Product    → Product Name
Customer   → Customer ID
Region     → Region
Profit     → Profit
```

## 10.4 Semantic Column Mapping

Different datasets can use different names for the same business concept.

For example:

```text
revenue
sales
sales_amount
total_amount
net_sales
```

may represent a sales metric.

Similarly:

```text
order_date
transaction_date
date
invoice_date
```

may represent the time dimension.

The Planner maps these columns into a normalized analytical schema.

Semantic mapping must include:

```text
Candidate meaning
Confidence
Evidence
```

Example:

```text
Column:
amount

Candidate meanings:
Sales / Cost / Profit

Confidence:
LOW

Action:
Do not silently assume
```

Low-confidence mappings should either:

- Be skipped
- Be sent for user confirmation

## 10.5 Capability Detection

The Planner determines which analytical capabilities are available.

Example:

```text
Product available?      YES
Customer available?     YES
Region available?       YES
Profit available?       YES
Date available?         YES
Sales available?        YES
```

## 10.6 Task Planning

Example:

```text
1. Clean data
2. Calculate KPIs
3. Analyze sales trends
4. Analyze products
5. Analyze customers
6. Analyze regions
7. Analyze profitability
8. Generate visualizations
9. Run forecasting
10. Generate insights
11. Generate recommendations
12. Generate report
```

## 10.7 Agent Routing

Example:

```text
IF Product exists:
    enable Product Analysis

IF Customer exists:
    enable Customer Analysis

IF Region exists:
    enable Regional Analysis

IF Profit exists:
    enable Profitability Analysis

IF Date + Sales exist
AND forecasting conditions are satisfied:
    enable Forecasting
ELSE:
    skip Forecasting
```

## 10.8 Output

```text
Schema Mapping
Capability Report
Analysis Plan
Agent Routing Decisions
Forecasting Eligibility
```

---

# 11. Agent 2 — Data Cleaning Agent

## 11.1 Purpose

The Data Cleaning Agent evaluates data quality and determines appropriate cleaning actions.

It should **not blindly clean every problem**.

Its internal workflow is:

```text
Detect Issue
    ↓
Classify Issue
    ↓
Collect Deterministic Evidence
    ↓
LLM Reasoning
    ↓
Recommend Action
    ↓
Risk Classification
    ↓
Policy Validation
    ↓
Human Approval if required
    ↓
Python Execution
    ↓
Validation
    ↓
Decision Logging
```

---

# 12. Data Cleaning Architecture

The cleaning process is divided into clear stages.

```text
                 DATA CLEANING AGENT
                         │
                         ▼
                 ISSUE DETECTION
                         │
                         ▼
                ISSUE CLASSIFICATION
                         │
                         ▼
              DETERMINISTIC EVIDENCE
                         │
                         ▼
                  LLM REASONING
                         │
                         ▼
               ACTION RECOMMENDATION
                         │
                         ▼
                  RISK CLASSIFIER
                         │
                         ▼
                POLICY VALIDATION
                         │
                         ▼
                  USER REVIEW
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
           APPROVE                 SKIP
              │                     │
              ▼                     ▼
       PYTHON EXECUTION         NO CHANGE
              │
              ▼
          VALIDATION
              │
              ▼
            LOGGING
```

---

# 13. Important Principle: Detection, Reasoning and Execution Are Separate

This is one of the most important design decisions in the system.

## Detection

Use deterministic tools:

```text
Pandas
NumPy
Statistics
Data-type inspection
Rule-based checks
```

Example:

```text
Sales column

Total rows = 10,000
Valid numeric values = 9,982
Invalid values = 18
```

## Reasoning

The LLM receives the detected evidence and reasons about possible strategies.

Example:

```text
Issue:
18 Sales values cannot be converted to numeric.

Possible actions:
- Remove rows
- Mark as missing
- Impute
- Request user decision

Recommendation:
Use median imputation only if the user approves.
```

## Execution

The LLM does not modify the DataFrame.

Python performs the approved action.

```text
LLM
 ↓
Recommendation

System Policy
 ↓
Risk

Human
 ↓
Approval

Python
 ↓
Execution
```

---

# 14. Missing-Value Detection

The Data Cleaning Agent calculates:

- Number of missing values
- Missing-value percentage
- Columns affected
- Potential analytical impact

Example:

```text
Region:
Missing = 3.2%
```

Potential recommendation:

```text
Fill with "Unknown"
```

For a critical numerical field:

```text
Sales:
Missing = 18%
```

the system should not blindly impute the values.

The action should be treated as higher risk.

---

# 15. Duplicate Detection

The Data Cleaning Agent should distinguish between:

### 15.1 Exact Duplicate

All fields are identical.

```text
Row 101:
1001 | Laptop | Mumbai | 50000

Row 102:
1001 | Laptop | Mumbai | 50000
```

This is a strong duplicate candidate.

Risk:

```text
LOW
```

---

### 15.2 Duplicate Identifier

Example:

```text
Order ID | Product
1001     | Laptop
1001     | Mouse
```

This is not necessarily a duplicate.

It may represent multiple line items belonging to one order.

Risk:

```text
MEDIUM / HIGH depending on context
```

The system should not automatically delete such rows.

---

### 15.3 Potential Duplicate Transaction

Two transactions may look highly similar:

```text
Customer
Date
Product
Amount
Region
```

but not be exactly identical.

The system can identify them as potential duplicates and use LLM reasoning to explain the evidence.

The LLM should not directly delete them.

Risk:

```text
HIGH
```

User approval is required.

---

# 16. Data-Type Validation

Examples:

```text
Order Date → object
```

Potential action:

```text
Convert to datetime
```

Another example:

```text
Sales → string
```

Potential processing:

```text
Remove currency symbols
Remove formatting
Convert to numeric
```

The actual conversion should be performed by deterministic Python code.

---

# 17. Invalid Values

Examples:

```text
Quantity = -5
Discount = 250%
```

The system should detect these using explicit rules.

Example:

```text
Discount < 0       → invalid
Discount > 100%    → suspicious/invalid
Quantity < 0       → suspicious/invalid
```

The system should not invent business rules without documenting them.

Where domain context is ambiguous, the issue should be flagged for review.

---

# 18. Numeric Conversion Example

Suppose:

```text
Price

₹450
₹500
free
N/A
₹400
TBD
₹450
```

Python first detects:

```text
Valid values = 4
Invalid values = 3
```

It calculates the median only from valid numerical values:

```text
400, 450, 450, 500

Median = 450
```

The LLM receives the structured evidence:

```text
Column:
Price

Invalid values:
free, N/A, TBD

Valid numeric count:
4

Invalid count:
3

Median:
₹450
```

The LLM can recommend:

```text
Replace invalid values with median ₹450.
```

But the system assigns:

```text
Risk = HIGH
Approval = REQUIRED
```

The user sees:

```text
Column: Price

3 values could not be converted:
"free", "N/A", "TBD"

4 values converted successfully.

Proposed action:
Replace the 3 invalid values with median ₹450.

Risk:
HIGH

[ Approve ] [ Skip ]
```

Only after approval does Python execute the modification.

---

# 19. Outlier Detection

Possible methods:

- IQR
- Z-score
- Robust statistical methods

The system must not assume:

```text
Statistical outlier = data error
```

Example:

```text
Sales = ₹950,000
```

This may be a legitimate high-value transaction.

Therefore:

```text
Statistical Detection
        ↓
Outlier detected
        ↓
Context / business reasoning
        ↓
Keep or propose removal
        ↓
High-risk removal requires approval
```

Deleting an outlier is a high-risk action.

---

# 20. Risk Classification

The cleaning workflow uses three risk levels.

## LOW RISK

Examples:

```text
Exact duplicate
Whitespace correction
Text formatting
Case standardisation
Currency-symbol removal
Simple formatting correction
```

Low-risk actions can follow predefined policy, but should still be logged.

## MEDIUM RISK

Examples:

```text
Missing categorical values
Type conversion
Date conversion
Categorical standardisation
```

Review is recommended.

## HIGH RISK

Examples:

```text
Deleting rows
Imputing Sales / Revenue
Removing suspected duplicate transactions
Deleting statistical outliers
```

**Explicit human approval is mandatory.**

Important:

> Risk level determines the required level of human oversight. It does not mean that an action is automatically correct or incorrect.

---

# 21. Policy Validation

The LLM should not decide its own permission level.

For example, the LLM cannot say:

```text
"Deleting these rows is low risk."
```

and cause the application to accept the deletion.

Instead:

```text
LLM
 ↓
Recommendation

Application Policy
 ↓
Risk Classification

Policy:
delete_rows → HIGH
 ↓
Approval Required
```

The policy is deterministic.

Example conceptual rules:

```python
if action == "delete_rows":
    risk = "HIGH"
    approval_required = True

elif action == "impute_sales":
    risk = "HIGH"
    approval_required = True

elif action == "fill_categorical_missing":
    risk = "MEDIUM"
    approval_required = True

elif action == "remove_whitespace":
    risk = "LOW"
    approval_required = False
```

---

# 22. Human-in-the-Loop Review

The UI should show a consolidated cleaning review rather than forcing the user through many separate screens.

Example:

| Issue | Column | Rows | Proposed Action | Risk | Decision |
|---|---|---:|---|---|---|
| Exact duplicates | — | 14 | Remove duplicates | LOW | ✓ |
| Missing values | Region | 32 | Fill "Unknown" | MEDIUM | ✓ |
| Type mismatch | Sales | 18 | Convert to numeric | MEDIUM | ✓ |
| Invalid Sales | Sales | 8 | Median ₹450 | HIGH | ☐ |
| Potential duplicates | Order ID | 5 | Review manually | HIGH | ☐ |
| Outliers | Sales | 7 | Remove | HIGH | ☐ |

Then:

```text
[ Apply Selected Actions ]
```

For high-risk actions, explicit approval is required.

---

# 23. Cleaning Decision Object

Each proposed action should be represented using a structured object.

Conceptually:

```text
CleaningDecision

issue_id
issue_type
column
affected_rows
evidence
detected_by
llm_reasoning
recommended_action
alternative_actions
confidence
risk_level
requires_approval
user_decision
execution_result
validation_result
```

Example:

```text
issue_id:
CLEAN-007

issue_type:
invalid_numeric

column:
Sales

affected_rows:
8

evidence:
8 values could not be converted to numeric

recommended_action:
replace_with_median

median:
450

confidence:
0.91

risk_level:
HIGH

requires_approval:
TRUE

user_decision:
APPROVED

execution_result:
8 values replaced

validation_result:
PASSED
```

This object can be stored in the shared agent state and decision log.

---

# 24. Python Execution

Once the user approves an action:

```text
Approved CleaningDecision
        ↓
Execution Function
        ↓
Pandas / NumPy
        ↓
DataFrame Modification
```

The LLM does not directly edit the DataFrame.

Example:

```python
if decision.approved:
    execute_cleaning_action(decision)
```

This makes the execution deterministic and testable.

---

# 25. Cleaning Validation

After execution, the system verifies the result.

Example:

```text
Before:

Sales dtype = object
Invalid numeric values = 18

        ↓
Cleaning

After:

Sales dtype = float64
Invalid numeric values = 0
```

Then:

```text
Validation:
PASS
```

If validation fails:

```text
Validation:
FAIL

        ↓
Do not continue blindly
        ↓
Return to Cleaning Agent
        ↓
Review / controlled retry
```

---

# 26. Cleaning Decision Log

Every material cleaning decision should be recorded.

Example:

```text
------------------------------------------------
Cleaning Decision
------------------------------------------------

Issue ID:
CLEAN-007

Issue:
Invalid numeric values

Column:
Sales

Affected Rows:
8

Evidence:
8 values could not be converted

Invalid Examples:
"free"
"N/A"
"TBD"

LLM Recommendation:
Replace with median

Computed Median:
₹450

Risk:
HIGH

Approval Required:
YES

User Decision:
APPROVED

Execution:
8 values replaced with ₹450

Validation:
PASSED
------------------------------------------------
```

This log supports:

- Debugging
- Reproducibility
- User transparency
- Research evaluation
- Viva demonstration
- Final report generation

---

# 27. Agent 3 — EDA Agent

## 27.1 Purpose

The EDA Agent determines and performs appropriate analytical procedures to understand sales performance.

## 27.2 KPI Analysis

### Sales KPIs

Depending on available fields:

- Total Revenue
- Total Orders
- Total Quantity
- Average Order Value
- Average Sales per Transaction
- Sales Growth

### Profitability KPIs

If profit exists:

- Total Profit
- Profit Margin
- Average Profit
- Revenue vs Profit

### Customer KPIs

If customer information exists:

- Number of customers
- Top customers
- Revenue contribution
- Customer concentration

### Product KPIs

- Top products
- Bottom products
- Category performance
- Product revenue contribution

## 27.3 Trend Analysis

If a valid date field exists:

- Daily trends
- Weekly trends
- Monthly trends
- Quarterly trends
- Yearly trends
- Month-over-month growth
- Year-over-year growth

Time granularity should depend on the available data.

## 27.4 Ranking Analysis

Examples:

```text
Top 10 products by revenue
Bottom 10 products by revenue
Top 10 customers
Top regions
Top categories
```

## 27.5 Regional Analysis

If geographic information exists:

- Revenue by region
- Profit by region
- Quantity by region
- Growth by region
- Regional contribution

## 27.6 Profitability Analysis

If Sales and Profit exist:

```text
Revenue
Profit
Profit Margin
Discount
```

Possible analysis:

- High revenue / low profit products
- High profit / low revenue products
- Discount vs profit
- Category profitability
- Regional profitability

## 27.7 Correlation Analysis

Correlation is performed only when suitable numerical variables exist.

Possible variables:

```text
Sales
Profit
Quantity
Discount
Cost
```

Correlation should be described as association, not automatically as causation.

## 27.8 Anomaly Preparation

The EDA Agent can identify:

- Sudden sales drops
- Unusual spikes
- Unusual product behaviour
- Unusual regional performance
- Abrupt KPI changes

---

# 28. EDA Feedback Loop

The system is not required to follow a rigid one-way pipeline.

Example:

```text
EDA Agent
    ↓
Data quality problem discovered
    ↓
Data Cleaning Agent
    ↓
Cleaning / correction
    ↓
Validation
    ↓
EDA Agent again
```

Example:

```text
EDA detects:
12% of dates cannot be interpreted

        ↓

Cleaning Agent
        ↓
Date normalization
        ↓
Validation
        ↓
EDA reruns
```

Feedback loops must have retry limits to prevent infinite execution.

---

# 29. Agent 4 — Visualization Agent

## 29.1 Purpose

The Visualization Agent determines how analytical results should be represented visually.

It considers:

- Analytical objective
- Data type
- Number of categories
- Number of observations
- Comparison requirements
- Trend requirements
- Distribution requirements
- Relationship requirements

## 29.2 Visualization Selection

| Analytical Objective | Recommended Visualization |
|---|---|
| Monthly sales trend | Line chart |
| Product comparison | Bar chart |
| Regional comparison | Bar chart |
| Revenue distribution | Histogram |
| Outlier analysis | Box plot |
| Sales vs Profit | Scatter plot |
| Numerical correlation | Heatmap |
| Category contribution | Bar / Donut chart |
| Forecast | Line chart with forecast |
| KPI summary | KPI cards |

## 29.3 Chart Workflow

```text
Verified EDA Results
        ↓
Determine chart requirements
        ↓
Select visualization
        ↓
Generate chart
        ↓
Add title and labels
        ↓
Validate chart
        ↓
Store chart metadata
```

The LLM can assist with selecting appropriate visualizations, but actual chart generation should use deterministic visualization libraries.

---

# 30. Agent 5 — Forecasting Agent

## 30.1 Purpose

The Forecasting Agent predicts future sales only when forecasting is analytically appropriate.

Forecasting must not automatically run for every dataset.

## 30.2 Forecast Eligibility

The system checks:

```text
Date/time column exists?
        AND
Sales/revenue metric exists?
        AND
Historical observations sufficient?
        AND
Time series can be ordered consistently?
        AND
Data quality acceptable?
```

If not:

```text
Forecasting → SKIPPED
```

The system should provide an explicit reason.

Example:

```text
Forecasting skipped:
No usable date field detected.
```

## 30.3 Forecasting Workflow

```text
Historical Sales
      ↓
Time-Series Preparation
      ↓
Train / Validation Split
      ↓
Candidate Models
      ↓
Model Evaluation
      ↓
Best Model Selection
      ↓
Future Forecast
```

## 30.4 Candidate Models

Depending on project scope:

- Naive baseline
- Moving average
- Exponential Smoothing
- ARIMA / SARIMA
- Machine-learning forecasting model

The project does not need to implement every model.

## 30.5 Model Evaluation

Possible metrics:

```text
MAE
RMSE
MAPE where appropriate
```

A naive baseline should be included.

Example:

```text
Model              MAE
-----------------------
Naive              1200
Exponential         980
ARIMA               850
```

Selected model:

```text
ARIMA
```

---

# 31. Agent 6 — Insight Agent

## 31.1 Purpose

The Insight Agent transforms verified analytical results into understandable business insights.

The distinction is:

```text
EDA Agent:
"What does the data calculate?"

Insight Agent:
"What does the result mean?"
```

## 31.2 Grounded Insight Architecture

```text
RAW DATA
   ↓
Python / Statistical Tools
   ↓
VERIFIED RESULTS
   ↓
INSIGHT AGENT
   ↓
GROUNDED INSIGHTS
```

The Insight Agent must not invent numerical values.

Example:

```text
Python calculates:
Revenue Growth = 18.4%
```

The Insight Agent may explain:

```text
Revenue increased by 18.4% compared with the previous period.
```

It must not invent:

```text
Revenue increased by 25%.
```

## 31.3 Insight Categories

Possible insights include:

- Sales trends
- Product performance
- Customer concentration
- Regional performance
- Profitability
- Discount effects
- Forecast patterns
- Anomaly explanations

The system should avoid unsupported causal claims.

---

# 32. Agent 7 — Recommendation Agent

## 32.1 Purpose

The Recommendation Agent converts validated insights into potential business actions.

The distinction is:

```text
Insight:
What happened?

Recommendation:
What could the business do?
```

## 32.2 Recommendation Categories

### Product

- Review declining products.
- Investigate low-profit products.
- Increase inventory for consistently high-demand products.
- Review underperforming categories.

### Customer

If customer data exists:

- Identify high-value customers.
- Prioritize retention efforts.
- Investigate customer concentration.

### Regional

- Investigate low-performing regions.
- Increase focus on high-growth regions.
- Compare regional product demand.

### Pricing / Discount

If discount data exists:

- Investigate high-discount, low-margin products.
- Review whether discounts appear associated with sufficient sales performance.

### Risk

Examples:

- Revenue concentration
- Declining products
- Regional decline
- Profitability deterioration
- Forecast decline

## 32.3 Recommendation Grounding

The workflow should be:

```text
Evidence
   ↓
Insight
   ↓
Business Implication
   ↓
Recommendation
```

Example:

```text
Evidence:
Product X revenue declined 25%.

        ↓

Insight:
Product X has experienced a sustained decline.

        ↓

Implication:
The product may be losing demand or competitiveness.

        ↓

Recommendation:
Investigate pricing, inventory, competition and customer
demand before deciding whether to discontinue or promote it.
```

The system should not pretend to know the exact business cause if the dataset cannot establish it.

---

# 33. Agent 8 — Report Agent

## 33.1 Purpose

The Report Agent consolidates validated outputs into a structured sales intelligence report.

## 33.2 Report Structure

### Section 1 — Executive Summary

- Overall sales performance
- Major trends
- Major risks
- Major opportunities
- Forecast summary, if available

### Section 2 — Dataset Overview

- Number of records
- Number of columns
- Date range
- Detected dimensions
- Detected measures

### Section 3 — Data Quality

- Missing values
- Duplicates
- Data-type corrections
- Outliers
- Cleaning actions
- Cleaning decision log

### Section 4 — Sales KPIs

- Revenue
- Orders
- Quantity
- Average Order Value
- Profit where available
- Growth

### Section 5 — Sales Trends

- Monthly / quarterly trends
- Growth patterns
- Major changes

### Section 6 — Product Analysis

- Top products
- Bottom products
- Category performance

### Section 7 — Customer Analysis

Only when customer information exists.

### Section 8 — Regional Analysis

Only when regional/geographic information exists.

### Section 9 — Profitability

Only when required fields exist.

### Section 10 — Forecast

Only when forecasting successfully executes.

### Section 11 — Key Insights

Ranked significant findings.

### Section 12 — Recommendations

Evidence-based actions.

### Section 13 — Limitations

The report explicitly states:

- Missing dimensions
- Data limitations
- Forecast limitations
- Analytical assumptions
- Model limitations
- Important cleaning decisions

---

# 34. Validation Architecture

Validation is not only a final step.

It occurs throughout the workflow.

## 34.1 Data Validation

Check:

- Required fields
- Data types
- Missing-value policy
- Duplicate policy
- Numeric validity
- Date validity

## 34.2 Cleaning Validation

Check:

- Approved actions only were executed
- Expected number of rows changed
- Data types after transformation
- Invalid values after conversion
- Duplicate policy after execution

## 34.3 Analytical Validation

Check:

- KPI calculations
- Aggregations
- Rankings
- Growth calculations
- Correlation inputs

## 34.4 Forecast Validation

Check:

- Chronological split
- Naive baseline
- MAE
- RMSE
- MAPE where appropriate
- Model-selection consistency

## 34.5 Visualization Validation

Check:

- Source data
- Aggregation
- Labels and units
- Chart suitability
- Impossible or misleading values

## 34.6 Insight Validation

Check:

- Every numerical claim exists in verified evidence
- No unsupported causal claim
- Insight is consistent with analytical results

## 34.7 Recommendation Validation

Check:

- Recommendation is supported by an insight
- Recommendation does not invent evidence
- Limitations are disclosed

---

# 35. Decision Traceability

Every important routing or analytical decision should record:

```text
Decision
Reason
Evidence / Preconditions
Action
Result
Validation Status
```

For cleaning, the trace should additionally record:

```text
Risk
LLM Recommendation
User Decision
```

Example:

```text
Decision:
Skip forecasting

Reason:
No usable date field

Action:
Do not execute Forecasting Agent

Validation:
Passed
```

Another example:

```text
Decision:
Run regional analysis

Reason:
Region column detected with acceptable quality

Action:
Execute regional analysis

Validation:
Passed
```

Another example:

```text
Decision:
Replace invalid Sales values

Reason:
8 values could not be converted to numeric

Evidence:
Invalid values = 8
Median of valid values = ₹450

Risk:
HIGH

Recommendation:
Median imputation

User Decision:
APPROVED

Action:
8 values replaced

Validation:
Passed
```

---

# 36. Complete End-to-End Workflow

```text
1. User uploads Sales CSV
            ↓
2. Planner Agent inspects schema
            ↓
3. Planner identifies analytical capabilities
            ↓
4. Planner creates execution plan
            ↓
5. Data Cleaning Agent detects data-quality issues
            ↓
6. Cleaning issues are classified
            ↓
7. Deterministic evidence is calculated
            ↓
8. LLM reasons about detected issues
            ↓
9. Cleaning recommendations are generated
            ↓
10. Risk level is assigned by system policy
            ↓
11. Approval requirement is determined
            ↓
12. User reviews medium/high-risk actions
            ↓
13. Approved actions are executed by Python
            ↓
14. Cleaning results are validated
            ↓
15. Cleaning decisions are logged
            ↓
16. EDA Agent performs appropriate analysis
            ↓
17. EDA checks whether additional cleaning is required
            ↓
18. If required → Cleaning Agent → Validation → EDA
            ↓
19. Visualization Agent selects and generates charts
            ↓
20. Planner/Forecasting logic checks forecasting eligibility
            ↓
21. Forecasting Agent runs only when applicable
            ↓
22. Forecast results are validated
            ↓
23. Insight Agent interprets verified results
            ↓
24. Insight results are validated
            ↓
25. Recommendation Agent creates evidence-based actions
            ↓
26. Recommendations are validated
            ↓
27. Report Agent consolidates validated outputs
            ↓
28. Final Sales Intelligence Report
            ↓
29. Decision Trace / Logs stored
```

---

# 37. What Makes This an Agentic System?

The project should not claim that multiple Python modules automatically make it agentic.

Agentic behaviour comes from:

## Perception

Agents inspect:

- Dataset
- Schema
- Data quality
- Analytical results

## Reasoning

Agents determine:

- What needs to be done
- Which method is appropriate
- Whether a task should execute
- Whether additional processing is required

## Tool Use

Agents can invoke:

- Pandas
- NumPy
- Statistical libraries
- Visualization libraries
- Forecasting libraries
- LLM services
- Report-generation tools

## Planning

The Planner Agent creates the workflow.

## Routing

The workflow conditionally executes or skips agents.

## Feedback

The workflow can return to earlier stages when validation identifies a problem.

## Shared State

Agents communicate through structured state.

---

# 38. LLM vs Conventional Analytics

The project should not use an LLM for calculations that can be performed deterministically.

## LLM / AI reasoning should handle

- Schema interpretation
- Semantic column mapping
- Planning
- Task selection
- Cleaning strategy recommendation
- Visualization selection
- Insight generation
- Recommendation generation
- Report synthesis

## Python / Statistical Tools should handle

- Mean
- Median
- Standard deviation
- Aggregations
- Correlations
- Growth calculations
- Ranking
- Data cleaning execution
- Chart generation
- Forecast calculations
- Forecast evaluation
- Validation

This separation improves numerical reliability and reproducibility.

---

# 39. Example: Complete Cleaning Decision

Suppose the uploaded dataset contains:

```text
Order ID | Product | Sales | Region
------------------------------------------------
1001     | Laptop  | ₹500 | West
1002     | Mouse   | ₹200 | West
1003     | Keyboard| free | NULL
1004     | Monitor | ₹800 | North
1004     | Monitor | ₹800 | North
```

The Data Cleaning Agent detects:

```text
Issue 1:
Sales contains "free"

Issue 2:
Region contains NULL

Issue 3:
Two rows are exact duplicates
```

The system creates:

```text
Issue 1
Sales → invalid numeric
Risk → HIGH
Recommendation → replace / mark missing
Approval → REQUIRED

Issue 2
Region → missing categorical
Risk → MEDIUM
Recommendation → Unknown
Approval → REQUIRED / policy controlled

Issue 3
Exact duplicate
Risk → LOW
Recommendation → remove duplicate
```

The user reviews:

```text
✓ Remove exact duplicate
✓ Fill Region with Unknown
☐ Handle invalid Sales
```

Only approved actions execute.

Then validation checks:

```text
Sales:
Still contains invalid values → YES

Region:
Missing values → 0

Duplicates:
Exact duplicates → 0
```

Because Sales still has an unresolved problem, the system records:

```text
Remaining Issue:
Invalid Sales value

EDA:
May require further cleaning
```

The system can return to the Cleaning Agent before continuing with analyses that depend on valid Sales values.

---

# 40. Example: Duplicate Reasoning

Suppose:

```text
Order ID | Customer | Product | Sales
--------------------------------------
1001     | Rahul    | Laptop  | 50000
1001     | Rahul    | Mouse   | 2000
```

The deterministic system detects:

```text
Repeated Order ID = TRUE
```

But:

```text
Rows are not identical
Products are different
Sales values are different
```

The system should **not delete either row**.

The LLM can provide:

```text
Reasoning:
The repeated Order ID appears consistent with a
multi-line-item order because the products differ.

Recommendation:
Retain both rows.
```

Risk:

```text
HIGH if deletion is proposed
```

Action:

```text
Keep
```

This demonstrates why duplicate detection and duplicate deletion must not be treated as the same operation.

---

# 41. Example: Outlier Reasoning

Suppose:

```text
Sales:

450
500
480
520
950000
```

Python detects:

```text
950000 → statistical outlier
```

The LLM receives the evidence.

It can recommend:

```text
The value is statistically unusual but may represent
a legitimate high-value transaction. Do not remove it
without additional evidence.
```

The system therefore recommends:

```text
Action:
Keep

Risk:
HIGH if deletion is considered
```

This prevents the common mistake:

```text
Outlier = Error
```

---

# 42. Failure and Exception Handling

The system should explicitly handle failures.

## No Sales Column

```text
Planner:
Sales metric not detected.

Action:
Skip sales-specific analysis or request compatible
column mapping.
```

## No Date Column

```text
Forecasting:
Skipped.

Reason:
No usable time dimension.
```

## Insufficient Observations

```text
Forecasting:
Skipped.

Reason:
Insufficient historical observations.
```

## Poor Data Quality

```text
Cleaning
   ↓
EDA
   ↓
Quality problem
   ↓
Cleaning
   ↓
Validation
   ↓
EDA
```

The workflow must have retry limits.

## Missing Customer Column

```text
Customer Analysis:
Skipped.

Reason:
No customer-identifying field detected.
```

The system should prefer skipping unsupported analysis over fabricating results.

---

# 43. Technology Architecture

A possible implementation stack:

```text
Frontend
   ↓
Streamlit
   ↓
Python Backend
   ↓
LangGraph
   ↓
Eight Specialized Agents
   ↓
LLM + Analytical Tools
   ↓
Pandas / NumPy / Scikit-learn /
Statsmodels / Plotly / Matplotlib
   ↓
Report Generation
```

## Suggested responsibilities

### Python

Core application logic.

### Pandas / NumPy

Data processing and numerical calculations.

### Scikit-learn

Machine-learning utilities and evaluation.

### Statsmodels

Statistical forecasting where appropriate.

### Plotly / Matplotlib

Visualization.

### LangGraph

Agent orchestration and shared state.

### LangChain

LLM/tool integration where useful.

### LLM

Reasoning, semantic interpretation, planning, recommendations and natural-language generation.

### Streamlit

User interface and human-in-the-loop review.

---

# 44. Recommended Project Structure

A possible implementation structure is:

```text
sales-intelligence-system/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
│
├── agents/
│   ├── planner_agent.py
│   ├── cleaning_agent.py
│   ├── eda_agent.py
│   ├── visualization_agent.py
│   ├── forecasting_agent.py
│   ├── insight_agent.py
│   ├── recommendation_agent.py
│   └── report_agent.py
│
├── workflow/
│   ├── graph.py
│   ├── state.py
│   ├── routing.py
│   └── policies.py
│
├── cleaning/
│   ├── detection.py
│   ├── decisions.py
│   ├── execution.py
│   ├── validation.py
│   └── duplicate_detection.py
│
├── analytics/
│   ├── kpis.py
│   ├── trends.py
│   ├── rankings.py
│   ├── profitability.py
│   └── correlations.py
│
├── forecasting/
│   ├── eligibility.py
│   ├── preprocessing.py
│   ├── models.py
│   └── evaluation.py
│
├── visualization/
│   ├── chart_selector.py
│   └── chart_generator.py
│
├── reporting/
│   ├── report_generator.py
│   └── templates/
│
├── logs/
│   └── decision_logs/
│
└── data/
    └── sample/
```

The exact structure can change during implementation, but the eight agent names should remain stable.

---

# 45. Security and Data Considerations

Sales datasets may contain sensitive business information.

The system should consider:

- Access control
- Data privacy
- Temporary file handling
- Removal of unnecessary customer identifiers
- Secure API-key management
- No hard-coded credentials
- Logging without exposing sensitive data
- Controlled LLM data transmission

The academic prototype should document:

```text
What data is sent to the LLM?
Why is it sent?
How is it protected?
```

API keys should be stored in environment variables rather than hard-coded into source code.

Example:

```text
.env
```

should not be committed to Git.

---

# 46. Research Evaluation Framework

The project should be evaluated experimentally.

## 46.1 Data Cleaning

Measure:

- Missing-value handling accuracy
- Duplicate detection accuracy
- Data-type detection accuracy
- Incorrect cleaning rate
- Human approval rate for high-risk actions

## 46.2 EDA

Measure:

- Numerical correctness
- KPI correctness
- Aggregation correctness
- Ranking correctness

## 46.3 Visualization

Evaluate:

- Chart appropriateness
- Readability
- Analytical relevance

## 46.4 Forecasting

Use:

```text
MAE
RMSE
MAPE where appropriate
```

Compare against a naive baseline.

## 46.5 Insight Quality

Human evaluators can score:

```text
Accuracy
Groundedness
Relevance
Clarity
Consistency
```

## 46.6 Recommendation Quality

Evaluate:

```text
Evidence support
Relevance
Actionability
Specificity
Unsupported-claim rate
```

## 46.7 System-Level Metrics

Measure:

```text
Execution time
Manual interventions
Task completion rate
Failure rate
Number of LLM calls
Token usage / cost
```

---

# 47. Baseline Comparison

A useful research comparison is:

```text
Baseline A
Manual Analysis

        vs

Baseline B
Single LLM Workflow

        vs

Proposed System
Planner + Eight Agents + Validation
+ Conditional Routing + Grounded Evidence
```

Compare:

- Time
- User effort
- Accuracy
- Analytical coverage
- Groundedness
- Reproducibility
- Failure rate

The purpose is to determine whether the multi-agent architecture actually provides measurable value.

---

# 48. Ablation Study

Where feasible, compare:

```text
A — Single LLM

B — Multi-agent without Planner

C — Multi-agent with Planner

D — Planner + Validation

E — Planner + Validation + Feedback
```

Compare:

```text
Accuracy
Groundedness
Task coverage
Manual effort
Execution time
Failure rate
```

The objective is to determine whether the architectural components contribute measurable improvements.

---

# 49. Limitations

The system should explicitly acknowledge:

1. Forecasting quality depends on historical data quality and quantity.
2. LLM-generated reasoning can still contain errors.
3. Semantic column detection can fail on unusual schemas.
4. Recommendations are decision support, not guaranteed business outcomes.
5. Correlation does not establish causation.
6. Different datasets may require different domain assumptions.
7. External LLM/API availability can affect execution.
8. Large datasets may require sampling or optimization.
9. Customer analysis depends on customer information being available.
10. Regional analysis depends on geographic information being available.
11. Human approval can reduce full automation, but improves control over high-risk actions.
12. The system's cleaning recommendations depend on the evidence available in the dataset.

Acknowledging these limitations increases the academic credibility of the project.

---

# 50. What the Project Should NOT Claim

Avoid claims such as:

```text
"Power BI cannot perform sales analysis."

"ChatGPT cannot analyse CSV files."

"This is the first multi-agent sales system."

"The system completely replaces a human analyst."

"LLMs perform all calculations."

"Every dataset can be forecast."

"Every generated recommendation is guaranteed to be correct."

"AI automatically knows which data should be deleted."
```

These claims are difficult to defend.

The project should instead focus on:

```text
Autonomous analytical orchestration
+
Specialized agents
+
Conditional routing
+
LLM reasoning
+
Deterministic analytics
+
Human-controlled high-risk cleaning
+
Validation
+
Grounded insights
+
Evidence-based recommendations
+
Traceability
```

---

# 51. What Makes the Proposed System Different

The strongest positioning is:

```text
Domain-specific Sales Intelligence
              +
Dynamic Task Planning
              +
Eight Specialized Agents
              +
Conditional Agent Routing
              +
Tool-Based Analytics
              +
Risk-Aware Data Cleaning
              +
Human-in-the-Loop High-Risk Decisions
              +
Forecasting When Applicable
              +
Grounded Insight Generation
              +
Evidence-Based Recommendations
              +
Automated Reporting
              +
Decision Traceability
```

The novelty should not be claimed as simply:

> "We used multi-agent AI."

The research contribution should focus on the architecture and its measurable behaviour.

---

# 52. Power BI Comparison

Power BI and other BI platforms already provide extensive capabilities for:

- Data transformation
- Data modelling
- Visualization
- Dashboards
- Business intelligence
- AI-assisted analysis
- Forecasting in applicable scenarios

Therefore, the project should not claim that conventional BI tools cannot perform sales analysis.

The distinction is:

```text
Traditional BI:

Data
 ↓
Model
 ↓
Dashboard
 ↓
Human Exploration


Proposed System:

Data
 ↓
Planner
 ↓
Specialized Agents
 ↓
Conditional Decisions
 ↓
Validation
 ↓
Insights
 ↓
Recommendations
 ↓
Report
```

The research focus is **autonomous analytical orchestration and decision support**, not dashboard creation alone.

---

# 53. ChatGPT / Single-LLM Comparison

A general-purpose LLM can analyse a CSV when provided with suitable prompts:

```text
"Clean this dataset."

"Perform EDA."

"Find top products."

"Analyse regions."

"Forecast sales."

"Give recommendations."

"Create a report."
```

The difference is orchestration.

### Prompt-Driven Workflow

```text
User
 ↓
Prompt
 ↓
LLM
 ↓
Response
 ↓
User decides next prompt
 ↓
LLM
```

### Proposed Workflow

```text
User
 ↓
Sales CSV
 ↓
Planner Agent
 ↓
Dynamic Workflow
 ↓
Eight Specialized Agents
 ↓
Validation
 ↓
Insights
 ↓
Recommendations
 ↓
Report
```

The proposed system reduces the need for the user to manually orchestrate each analytical step.

---

# 54. Final System Output

The system should produce:

```text
                    SALES INTELLIGENCE
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      Dashboard          Charts         PDF Report
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    Business Insights
                           │
                           ▼
                     Recommendations
                           │
                           ▼
                  Forecast if applicable
                           │
                           ▼
                    Decision Trace
```

The final output should clearly distinguish:

```text
Data-derived facts
        ↓
Analytical results
        ↓
LLM interpretation
        ↓
Recommendations
```

---

# 55. Final Architecture Principle

The complete system follows:

```text
DATA
  ↓
PERCEIVE
  ↓
PLAN
  ↓
DECIDE
  ↓
DETECT
  ↓
REASON
  ↓
RECOMMEND
  ↓
RISK CHECK
  ↓
HUMAN APPROVAL
  ↓
EXECUTE
  ↓
VALIDATE
  ↓
ANALYSE
  ↓
INTERPRET
  ↓
RECOMMEND
  ↓
REPORT
  ↓
LOG
```

The workflow should be **adaptive rather than blindly sequential**.

The Planner decides what is required.

Each specialized agent decides how its bounded task should be performed.

The Data Cleaning Agent detects problems using deterministic methods, uses LLM reasoning where useful, assigns recommendations, applies risk-aware policy, obtains human approval for high-risk actions, executes approved changes using Python, validates the results and records the decision.

The workflow can skip irrelevant tasks.

The workflow can return to earlier stages when validation detects a problem.

Numerical claims originate from deterministic analytical results.

LLMs primarily provide reasoning, interpretation, planning, semantic understanding and natural-language generation.

---

# 56. Final Definition

> **The AI-Powered Multi-Agent Sales Intelligence System is a domain-specific Agentic AI decision-support system for retail and e-commerce sales analytics. It autonomously inspects sales datasets, determines applicable analytical tasks, delegates those tasks to eight specialized agents, combines LLM reasoning with deterministic analytical tools, performs risk-aware data cleaning with human approval for high-risk mutations, applies forecasting when appropriate, validates intermediate and final results, generates evidence-grounded insights and recommendations, and consolidates the results into an automated sales intelligence report with complete decision traceability.**

The key claim is **not** that the system makes every business decision autonomously.

The defensible claim is:

> **The system autonomously coordinates a bounded set of analytical decisions and provides traceable, evidence-grounded decision support while retaining human control over high-risk data modifications.**

---

# 57. Final Red-Team Checklist

Before declaring the implementation complete:

```text
[ ] Exactly eight agents are implemented.
[ ] Each agent has a clearly bounded responsibility.
[ ] Planner performs schema and capability detection.
[ ] Semantic mappings have confidence handling.
[ ] Unsupported tasks are skipped with explicit reasons.
[ ] Numerical calculations use deterministic tools.
[ ] Cleaning uses deterministic issue detection.
[ ] LLM is used for reasoning/recommendation, not direct DataFrame mutation.
[ ] Cleaning actions have risk levels.
[ ] LOW/MEDIUM/HIGH risk policy is deterministic.
[ ] High-risk actions require explicit human approval.
[ ] User can approve or skip proposed cleaning actions.
[ ] Exact duplicates are distinguished from repeated legitimate transactions.
[ ] Statistical outliers are not blindly deleted.
[ ] Invalid numeric values are handled through preview/recommendation/approval.
[ ] Cleaning execution is performed by Python.
[ ] Cleaning results are validated.
[ ] Cleaning decisions are logged.
[ ] EDA can trigger a controlled feedback loop.
[ ] Feedback loops have retry limits.
[ ] Visualization selection is data-driven.
[ ] Forecasting has explicit eligibility checks.
[ ] Forecasting uses chronological validation.
[ ] Forecasting has a naive baseline.
[ ] Model selection uses validation metrics.
[ ] Insights are grounded in structured evidence.
[ ] Unsupported causal claims are rejected or qualified.
[ ] Recommendations contain evidence and limitations.
[ ] Report generation uses validated outputs.
[ ] Errors and warnings are surfaced to the user.
[ ] Important routing decisions are logged.
[ ] Security and privacy controls are documented.
[ ] Baseline comparison is performed.
[ ] Ablation study is performed where feasible.
[ ] Reproducibility information is recorded.
[ ] System limitations are documented.
```

---

# 58. Final Positioning Statement

For the synopsis, presentation, viva and research paper, position the project as:

> **An adaptive, domain-specific multi-agent sales analytics and decision-support system that autonomously plans and routes heterogeneous retail/e-commerce sales-analysis tasks, combines LLM reasoning with deterministic analytics, performs risk-aware human-in-the-loop data cleaning, conditionally performs forecasting, validates intermediate and final results, and generates evidence-grounded business intelligence with minimal manual orchestration.**
