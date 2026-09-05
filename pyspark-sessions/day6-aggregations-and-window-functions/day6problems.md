# Day 6 Problems — GroupBy, Aggregations, Sorting, Date Functions

Use the `sales.csv` dataset from `data/` for all problems.

---

## Section 1 — groupBy + Aggregations

**Problem 1**
Find the total number of sales and total revenue per salesperson.
Sort by total revenue descending.

**Problem 2**
For each region, find:
- Number of sales
- Total quantity sold
- Average unit price (rounded to 2 decimal places)

**Problem 3**
Find the most expensive product (by unit_price) sold in each category.

**Problem 4**
For each salesperson, find how many distinct categories they have sold in.
Show only salespersons who sold in more than 2 categories. *(HAVING)*

**Problem 5**
Group by region and status. Show the count and total revenue for each combination.

**Problem 6**
For each category, collect the list of all unique products sold (no duplicates).

---

## Section 2 — Filter After groupBy (HAVING)

**Problem 7**
Find categories where the total quantity sold is more than 30 units.

**Problem 8**
Find salespersons whose average sale amount is above 20,000.

**Problem 9**
Find region + category combinations where more than 2 sales were made.

---

## Section 3 — orderBy / sort

**Problem 10**
List all sales sorted by sale_date ascending (oldest first).

**Problem 11**
Sort sales by total_amount descending. Show top 5.

**Problem 12**
Sort by region ascending, then by unit_price descending within each region.

**Problem 13**
Show the monthly revenue summary (year + month) sorted chronologically.

---

## Section 4 — Date Functions

**Problem 14**
Add a column `delivery_days` showing how many days each delivery took.
Find the sale with the longest delivery time.

**Problem 15**
Add a column `days_since_sale` showing how many days ago each sale happened (from today).

**Problem 16**
Add a column `expected_sla` = sale_date + 5 days. Flag orders where delivery_date > expected_sla as "SLA Breached".

**Problem 17**
Extract the quarter from sale_date. Show total revenue by quarter.

**Problem 18**
Format sale_date as "Month YYYY" (e.g., "January 2024"). Show revenue grouped by this label, sorted chronologically.

**Problem 19**
Find which day of the week most sales happen on. (Hint: dayofweek + groupBy + count)

**Problem 20**
Parse this string column into a proper DateType and calculate how many days ago it was:
`"15/03/2024"` — format is `dd/MM/yyyy`.
