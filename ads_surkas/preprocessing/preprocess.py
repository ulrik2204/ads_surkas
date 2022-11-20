# import numpy as np
import pandas as pd


def load_data(filename: str):
    return pd.read_csv(filename, low_memory=False)
    # data["Year"] = data["Year"].astype("int32")
    # data["Month"] = data["Month"].astype("int32")
    # data["Year"].fillna(0)
    # data["Year"].astype("int32")
    # data["Month"].fillna(0)
    # data["Month"].astype("int32")
    # data["Time"] = pd.to_datetime(
    #     data["Year"] + "-" + data["Month"], format="%Y-%m", errors="coerce"
    # )


def clean_data(df: pd.DataFrame):
    data = df.copy(deep=True)
    data = df[df["item_id"].notna()]
    data["Year"] = data["Year"].astype("int32")
    data["Month"] = data["Month"].astype("int32")
    data["Day"] = 1
    data["Time"] = pd.to_datetime(data[["Year", "Month", "Day"]])
    data["Customer Since"] = pd.to_datetime(data["Customer Since"])
    dat = data.filter(
        [
            "item_id",
            "status",
            "created_at",
            "sku",
            "Customer ID",
            "increment_id",
            "category_name_1",
            "sales_commission_code",
            "discount_amount",
            "payment_method",
            "Working Date",
            "BI Status",
            "MV",
            "Customer Since",
            "M-Y",
            "FY",
            "price",
            "qty_ordered",
            "grand_total",
            "Time",
            "Year",
            "Month",
        ]
    )
    return dat[~((dat["grand_total"] < 0) & (dat["status"] == "complete"))]
