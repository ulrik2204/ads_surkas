import math
from enum import Enum
from typing import Any, Dict, Tuple

import pandas as pd

from ..preprocessing import clean_data, load_data


class Optimality(Enum):
    OPTIMAL = "optimal"
    LOWER = "lower"
    HIGHER = "higher"


def find_lowest_threshold_id(value: float, thresholds: Dict[int, Dict[str, Any]]):
    """
    Returns the id of the lowest threshold group that value fits within.
    """
    lowest_threshold_id = None
    for i in range(len(thresholds)):
        threshold = thresholds[i]["threshold"]
        if value <= threshold or threshold == 0:
            lowest_threshold_id = i
            break
    return lowest_threshold_id


def get_group_optimality(
    groups: Dict[int, Dict[str, Any]], optimal_size: int
) -> Tuple[bool, bool, Dict[int, Optimality]]:
    """Returns a dict which keys that maps to groups of whether the group is optimal or not"""
    result = dict()
    n_groups = len(groups)
    for key, value in groups.items():
        size = len(value["items"])
        # optimality_score = Optimality.OPTIMAL if size == optimal_size else Optimality.HIGHER if size > optimal_size else Optimality.LOWER
        # result[key] = optimality_score
        result[key] = size - optimal_size
    # print("val", result.values())
    any_negatives = any(map(lambda val: val < 0, result.values()))
    optimal = sum(filter(lambda val: val > 0, result.values())) < n_groups
    return optimal, any_negatives, result


def remove_item_from_groups(
    groups: Dict[int, Dict[str, Any]], group_id: int, item_id: int
):
    deleted_item = groups[group_id]["items"][item_id]
    new_group_items = {
        key: value for key, value in groups[group_id]["items"].items() if key != item_id
    }
    new_group = {
        "threshold": new_group_items[max(new_group_items, key=new_group_items.get)],
        "items": new_group_items,
    }
    return {**groups, group_id: new_group}, deleted_item


def add_item_to_groups(
    groups: Dict[int, Dict[str, Any]], group_id: int, item_id: int, item_value: int
):
    threshold = groups[group_id]["threshold"]
    new_group_items = {**groups[group_id]["items"], item_id: item_value}
    new_group = {"threshold": max(threshold, item_value), "items": new_group_items}
    return {**groups, group_id: new_group}


def rearrange_groups(
    groups: Dict[int, Dict[str, Any]], group_optimality: Dict[int, Dict[str, bool]]
):

    # supply negative groups with items from positive groups
    positives = {key: value for key, value in group_optimality.items() if value > 0}
    negatives = {key: value for key, value in group_optimality.items() if value < 0}
    total_negatives = -1 * sum(map(lambda val: val[1], negatives.items()))
    print("total_neg", total_negatives)
    print(positives, negatives, group_optimality)
    item_bank = dict()
    changed = 0
    new_groups = groups
    for g_key, group in new_groups.items():
        RERUN = False

        def procedure():
            optimality = group_optimality[g_key]  # an int
            # take the "optimality" most
            if optimality < 0:
                for _ in range(optimality * -1):
                    print("Opt < 0")
                    print("opt", optimality, group)
                    print("item bank", item_bank)
                    if len(item_bank) == 0:
                        RERUN = True
                    lowest_item_id = min(item_bank, key=item_bank.get)
                    new_groups = add_item_to_groups(
                        new_groups, g_key, lowest_item_id, item_bank[lowest_item_id]
                    )
                    del item_bank[lowest_item_id]
                    changed -= 1
            elif optimality > 0 or changed > 0:
                changed_copy = changed
                for _ in range(changed_copy):
                    print(f"Opt{optimality} > 0 or changed add", changed)
                    lowest_item_id = min(item_bank, key=item_bank.get)
                    new_groups = add_item_to_groups(
                        new_groups, g_key, lowest_item_id, item_bank[lowest_item_id]
                    )
                    del item_bank[lowest_item_id]
                    changed -= 1
                    print("new low", new_groups, g_key, lowest_item_id)
                for _ in range(min(optimality + changed_copy, total_negatives)):
                    print(f"opt{optimality} > 0 or changed remove")
                    biggest_item_id = max(group["items"], key=group["items"].get)
                    new_groups, deleted_item = remove_item_from_groups(
                        new_groups, g_key, biggest_item_id
                    )
                    item_bank[biggest_item_id] = deleted_item
                    del group["items"][biggest_item_id]
                    changed += 1
                    print("new big", new_groups, g_key, biggest_item_id)
                    positives[g_key] -= 1
            # Distribute the bank to the negatives and move them accordingly

        procedure()
        if RERUN:
            procedure()

    return new_groups


def find_n_groups(df: pd.DataFrame, column: str, id_column: str, n_groups=5):
    """Function that finds the thresholds to split one column
    such that the rows are split in n_groups of the same size.

    Args:
        df (pd.DataFrame): DataFrame of data per entity
            that wants to be split up into groups.
        column (str): The column to split the rows by.
        n_groups (int, optional): Amount of groups to split by. Defaults to 5.
    """
    # n acts like an ID
    groups = {n: {"items": {}, "threshold": 0} for n in range(n_groups)}
    highest_threshold_id = n_groups - 1
    optimal_group_size = 0
    total_items = 0

    for _, row in df.iterrows():
        value = row[column]
        row_id = row[id_column]
        # Move the item into the correct group within the lowest threshold
        lowest_id = find_lowest_threshold_id(value, groups)
        if lowest_id is None:
            # If it is None, then the value doesn't fit within
            # any of the thresholds, so we have to extend the highest one
            groups[highest_threshold_id]["threshold"] = value
            groups[highest_threshold_id]["items"][row_id] = value
        else:
            groups[lowest_id]["items"][row_id] = value

        # adjust optimal group size
        total_items += 1
        optimal_group_size = total_items // n_groups
        is_optimal, any_negatives, optimal_groups = get_group_optimality(
            groups, optimal_group_size
        )
        print(groups)
        if not any_negatives:
            continue
            # raise Exception(f"Should not be able to be lower, groups={optimal_groups}")
        # Rearrange the groups and thresholds:
        # print("do something")
        groups = rearrange_groups(groups, optimal_groups)

        # Adjust the groups if the their count differs from the average by more than n_groups

    return sorted([x["threshold"] for x in groups.values()])


# find_n_groups(dat, "all_time_total", "Customer ID")
# lo = find_lowest_threshold_id(9, th)
# th[lo]
# opt = get_group_optimality(th, 8//3)


def main():

    data = clean_data(load_data("./.data/pakistan_ecommerce.csv"))
    dat = (
        data.groupby("increment_id")
        .first()
        .groupby("Customer ID", as_index=False)
        .agg(
            all_time_total=("grand_total", "sum"), order_count=("grand_total", "count")
        )
    )
    # da = dat.groupby("all_time_total")["order_count"].agg(all_time_total_count="count")
    df = pd.DataFrame(
        {
            "Customer ID": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"],
            "all_time_total": [1, 1, 3, 5, 10, 100, 1000, 2, 4, 7, 80, 900],
        }
    )
    groups = find_n_groups(df, "all_time_total", "Customer ID")
    print(groups)
    # groups = {
    #     0: {"threshold": 5, "items": {1: 1, 2: 3, 3: 4, 4: 4}},
    #     1: {"threshold": 10, "items": {6: 11, 7: 12}},
    #     2: {"threshold": 15, "items": {8: 13}},
    # }
    # print("groups", groups)
    # groups = add_item_to_groups(groups, 0, 5, 5)
    # print("add", groups)
    # a, b = remove_item_from_groups(groups, 0, 2)
    # print("remove", a, b)
    # is_optimal, any_negatives, group_optimality = get_group_optimality(groups, 7 // 3)
    # find_n_groups(df, "all_time_total", "Customer ID", n_groups=3)
    # print("negatives", any_negatives, group_optimality)
    # print("rearrange", rearrange_groups(groups, group_optimality))


if __name__ == "__main__":
    pd.options.mode.chained_assignment = None
    main()
