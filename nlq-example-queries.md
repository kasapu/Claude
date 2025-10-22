# Natural Language Query Examples - Executive Analytics

## Quick Reference for Business Users

This guide provides example natural language queries across common executive analytics scenarios. No SQL knowledge required!

---

## Customer & Revenue Analytics

### Customer Acquisition
```
✓ "What was our customer acquisition cost by channel last quarter?"
✓ "Show me new customer growth month by month this year"
✓ "Which marketing channels brought in the most high-value customers?"
✓ "What's our average customer lifetime value by acquisition source?"
```

### Revenue Performance
```
✓ "What was total revenue by product category in Q4?"
✓ "Show me year-over-year revenue growth by region"
✓ "Which products have the highest revenue per customer?"
✓ "What's our monthly recurring revenue trend for the last 12 months?"
```

### Customer Retention
```
✓ "What is our customer churn rate this quarter vs last quarter?"
✓ "Show me retention rate by customer segment"
✓ "Which customer cohort has the best 12-month retention?"
✓ "What percentage of customers made repeat purchases this year?"
```

---

## Financial Performance

### Profitability
```
✓ "What are our top 10 products by profit margin?"
✓ "Show me gross margin trend by quarter for the last 2 years"
✓ "Which business units are most profitable?"
✓ "What's our operating margin by region?"
```

### Cost Analysis
```
✓ "What are our largest expense categories this quarter?"
✓ "Show me cost per acquisition trend over the last 6 months"
✓ "Which departments exceeded their budget this year?"
✓ "What's our customer support cost per ticket by product?"
```

### Cash Flow
```
✓ "What's our accounts receivable aging summary?"
✓ "Show me days sales outstanding (DSO) trend"
✓ "What's our average payment collection time by customer segment?"
```

---

## Sales & Pipeline Analytics

### Sales Performance
```
✓ "Who are our top 10 sales reps by revenue this quarter?"
✓ "What's our average deal size by sales region?"
✓ "Show me win rate by sales stage"
✓ "What's our sales conversion rate from lead to customer?"
```

### Pipeline Health
```
✓ "What's the total value of deals in our pipeline by stage?"
✓ "Show me average time to close by deal size"
✓ "Which opportunities are at risk of churning this month?"
✓ "What's our sales velocity (deals closed per week) this quarter?"
```

---

## Operational Efficiency

### Order Fulfillment
```
✓ "What's our average order fulfillment time by warehouse?"
✓ "Which products have the longest delivery times?"
✓ "Show me on-time delivery rate by shipping carrier"
✓ "What's our order accuracy rate this month vs last month?"
```

### Inventory Management
```
✓ "Which products are currently out of stock?"
✓ "Show me inventory turnover rate by product category"
✓ "What's our carrying cost for slow-moving inventory?"
✓ "Which warehouses have excess inventory?"
```

### Customer Support
```
✓ "What's our average customer support ticket resolution time?"
✓ "Show me ticket volume by category this week"
✓ "What's our first response time trend over the last month?"
✓ "Which support agents have the highest customer satisfaction scores?"
```

---

## Product & Engagement Analytics

### Product Performance
```
✓ "Which features are most used in our app this month?"
✓ "Show me daily active users trend for the last quarter"
✓ "What's our product adoption rate for new features?"
✓ "Which products have the highest return rate?"
```

### User Engagement
```
✓ "What's our average session duration by user segment?"
✓ "Show me user engagement score by cohort"
✓ "Which pages have the highest bounce rate?"
✓ "What's our email open rate by campaign type?"
```

---

## Comparative & Trend Analysis

### Time Comparisons
```
✓ "Compare this quarter's revenue to the same quarter last year"
✓ "Show me month-over-month growth for the last 6 months"
✓ "What's our year-to-date performance vs target?"
✓ "How does this week's sales compare to the previous 4 weeks?"
```

### Segment Comparisons
```
✓ "Compare customer lifetime value across all segments"
✓ "Show me conversion rate by traffic source"
✓ "Which region has the highest revenue per employee?"
✓ "Compare product performance across different customer tiers"
```

---

## Advanced Multi-Metric Queries

### Combined KPIs
```
✓ "Show me revenue, profit margin, and customer count by product line"
✓ "What are our top 5 customers by revenue and their lifetime value?"
✓ "Compare sales, costs, and profitability across regions"
✓ "Show me customer acquisition cost, lifetime value, and payback period by channel"
```

### Cohort Analysis
```
✓ "Show me retention curve for customers acquired in Q1 2024"
✓ "What's the revenue contribution of each monthly cohort this year?"
✓ "Compare purchase behavior between new and returning customers"
```

---

## Tips for Better Queries

### Be Specific with Time Periods
❌ "Show me sales" (too vague)
✓ "Show me sales for last quarter"
✓ "Show me daily sales for the last 30 days"

### Specify Dimensions Clearly
❌ "Show me performance" (unclear metric)
✓ "Show me revenue by product category"
✓ "Show me conversion rate by traffic source"

### Use Business Terms
✓ "Customer lifetime value" instead of technical abbreviations
✓ "Last quarter" instead of "Q4 2024" (system understands context)
✓ "Year over year" or "month over month" for comparisons

### Request Multiple Metrics
✓ "Show me revenue and profit margin by region"
✓ "What are our top products by both volume and revenue?"

---

## Database-Specific Features

### When Using Snowflake
- Leverage fast aggregations on large datasets
- Use for complex analytics across multiple data sources

### When Using PostgreSQL
- Great for transactional data analysis
- Excellent JSON/array support for semi-structured data

### When Using MySQL
- Optimized for high-volume transactional queries
- Fast for straightforward aggregations

### When Using Databricks
- Best for big data analytics
- Leverage for machine learning-ready datasets

---

## Getting the Most Value

### Start Simple
1. Begin with single-metric queries
2. Add filters and dimensions gradually
3. Build up to complex multi-metric analysis

### Ask Follow-ups
After getting results, you can ask:
- "Show me the top 10 only"
- "Break this down by month"
- "Add profit margin to this analysis"
- "Filter for values over $10,000"

### Request Explanations
- "Explain how this calculation works"
- "What assumptions are used in this query?"
- "Why are these numbers different from last week?"

---

## Common Business Questions by Role

### CEO/CFO
- Revenue, profitability, and growth metrics
- Strategic KPIs and board-level reporting
- Cross-functional performance comparisons

### VP Sales
- Pipeline health and sales performance
- Win rates and deal velocity
- Sales team productivity

### VP Marketing
- Customer acquisition costs and channel performance
- Campaign ROI and conversion rates
- Customer segmentation and lifetime value

### VP Operations
- Fulfillment efficiency and inventory metrics
- Operational costs and resource utilization
- Quality metrics and process performance

### Customer Success
- Retention and churn metrics
- Customer health scores
- Support ticket analytics

---

## Real-Time Decision Making

This system enables instant answers to critical business questions:

**Before NLQ**: Request to analyst → Wait hours/days → Get static report → Ask follow-ups → Wait again

**With NLQ**: Ask question → Get answer in <5 seconds → Refine query → Make decision immediately

**Result**: 20-30% productivity increase and democratized data access for 80% of workforce

---

## Need Help?

If you're unsure how to phrase a question:
1. Start with "Show me..." or "What is..."
2. Specify the metric you want (revenue, count, average, etc.)
3. Add time period (last quarter, this year, etc.)
4. Add dimensions (by region, by product, etc.)

The system will ask clarifying questions if needed!
