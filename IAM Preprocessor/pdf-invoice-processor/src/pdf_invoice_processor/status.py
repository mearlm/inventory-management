def rollup_status(*statuses: str) -> str:
    if "ERROR" in statuses:
        return "ERROR"
    if "REVIEW" in statuses:
        return "REVIEW"
    return "READY"

def add_status_message(item: dict, message: str) -> None:
    if item["status_message"]:
        item["status_message"] += "; " + message
    else:
        item["status_message"] = message

def build_component_status_message(
    header_status: str,
    item_status: str,
    summary_status: str,
) -> str:
    messages = []

    if header_status != "READY":
        messages.append(f"Header: {header_status}")

    if item_status != "READY":
        messages.append(f"Items: {item_status}")

    if summary_status != "READY":
        messages.append(f"Summary: {summary_status}")

    return "; ".join(messages)
