def calculate_confidence(probability: float) -> str:
    """
    Convert prediction probability into a confidence level.
    """

    if probability >= 80:
        return "Very High"

    if probability >= 65:
        return "High"

    if probability >= 50:
        return "Medium"

    return "Low"