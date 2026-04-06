def get_priority_color(priority):
    mapping = {
        "P1": "danger",
        "P2": "warning",
        "P3": "primary",
        "P4": "secondary"
    }
    return mapping.get(priority, "light")