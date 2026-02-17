def auto_category(description):
    desc = description.lower()

    if any(word in desc for word in ["burger", "pizza", "restaurant", "food"]):
        return "Food"
    if any(word in desc for word in ["uber", "bus", "train", "fuel"]):
        return "Travel"
    if any(word in desc for word in ["amazon", "shopping", "cloth"]):
        return "Shopping"
    if any(word in desc for word in ["electricity", "rent", "bill"]):
        return "Bills"

    return "Other"
