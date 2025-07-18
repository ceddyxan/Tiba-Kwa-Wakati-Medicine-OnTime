import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def forecast_adherence_arima(adherence_history, steps=7):
    """
    Forecast future adherence using ARIMA.
    adherence_history: list or array of 0/1 (past adherence)
    steps: number of days to forecast
    Returns: forecasted adherence probabilities for next 'steps' days
    """
    series = pd.Series(adherence_history)
    # Fit ARIMA model (order can be tuned)
    model = ARIMA(series, order=(1, 0, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)
    # Clip to [0, 1] for probability interpretation
    return np.clip(forecast, 0, 1)

# Example usage:
if __name__ == "__main__":
    history = [1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0]
    forecast = forecast_adherence_arima(history, steps=7)
    print("Next 7 days adherence forecast:", forecast) 