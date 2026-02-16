import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

FILE = "expenses.csv"

df = pd.read_csv(FILE)

if df.empty:
    print("No data available for analysis.")
    exit()

# Convert Date column
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.month

# Monthly totals
monthly = df.groupby("Month")["Amount"].sum()

# Plot monthly expense
monthly.plot(kind="bar")
plt.title("Monthly Expense")
plt.xlabel("Month")
plt.ylabel("Total Spending")
plt.show()

# Prediction
X = np.array(monthly.index).reshape(-1, 1)
y = monthly.values

model = LinearRegression()
model.fit(X, y)

next_month = np.array([[max(monthly.index) + 1]])
prediction = model.predict(next_month)

print("\n📈 Predicted next month expense:", round(prediction[0], 2))
