import pandas as pd, numpy as np
df = pd.read_csv("cleaned_sales_dataset.csv", parse_dates=["Order_Date"])
pm, qm = df.Unit_Price.median(), df.Quantity.median()
def seg(r):
    hp, hq = r.Unit_Price >= pm, r.Quantity > qm
    return ("Big Spenders" if hp and hq else "Premium Single-Item" if hp else "Bulk Value Buyers" if hq else "Light Buyers")
df["Segment"] = df.apply(seg, axis=1)
print("median price", pm, "median qty", qm)
tot = df.Total_Sales.sum()
g = df.groupby("Segment").agg(orders=("Order_ID","count"), revenue=("Total_Sales","sum"), aov=("Total_Sales","mean"),
        avg_age=("Age","mean"), avg_qty=("Quantity","mean"), avg_price=("Unit_Price","mean"))
g["pct_orders"] = g.orders/len(df)*100; g["pct_revenue"] = g.revenue/tot*100
print(g.round(1).sort_values("revenue", ascending=False).to_string())
print(df.groupby("Segment").Category.agg(lambda s: s.value_counts(normalize=True).round(3).head(2).to_dict()))
print(df.groupby("Segment").City.agg(lambda s: s[s!="Unknown"].value_counts().head(2).to_dict()))
print(pd.crosstab(df.Segment, df.Age_Group, values=df.Total_Sales, aggfunc="sum", normalize="index").round(3))
print(pd.crosstab(df.Segment, df.Category, normalize="index").round(3))
# monthly growth
m = df[df.Order_Date<"2026-01-01"].groupby("Order_Month").Total_Sales.sum()
print((m.pct_change()*100).round(1).to_dict())
print("top cat share", df[df.Category=="Electronics"].Total_Sales.sum()/tot, "UPO", df.Quantity.mean())
df.to_csv("cleaned_sales_with_segments.csv", index=False)
g.round(2).to_csv("segment_summary.csv")
