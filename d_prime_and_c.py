import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from numpy.polynomial.polynomial import Polynomial

data_file_path = 'kalyanbrata_data.csv'  # Replace with your file path
experiment_data = pd.read_csv(data_file_path)

# Assume data is already loaded into 'experiment_data' DataFrame
# Sorted set sizes for consistent plotting
sorted_set_sizes = sorted(experiment_data['Set Size'].unique())

# Initialize lists to store d' and criterion values along with error calculations
d_prime_values = []
criterion_values = []
d_prime_errors = []
criterion_errors = []

# Loop through each set size to calculate d', criterion, and standard deviations for error bars
for set_size in sorted_set_sizes:
    # Filter data for the current set size
    set_data = experiment_data[experiment_data['Set Size'] == set_size]
    
    # Calculate hits, misses, false alarms, and correct rejections
    hits = set_data[(set_data['Is Target'] == True) & 
                    (set_data['Participant Response'] == 'Yes')].shape[0]
    misses = set_data[(set_data['Is Target'] == True) & 
                      (set_data['Participant Response'] == 'No')].shape[0]
    false_alarms = set_data[(set_data['Is Target'] == False) & 
                            (set_data['Participant Response'] == 'Yes')].shape[0]
    correct_rejections = set_data[(set_data['Is Target'] == False) & 
                                  (set_data['Participant Response'] == 'No')].shape[0]
    
    # Calculate hit rate and false alarm rate
    hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
    false_alarm_rate = false_alarms / (false_alarms + correct_rejections) if (false_alarms + correct_rejections) > 0 else 0
    
    # Handle extreme rates by clipping to avoid issues with z-scores
    hit_rate = np.clip(hit_rate, 0.01, 0.99)
    false_alarm_rate = np.clip(false_alarm_rate, 0.01, 0.99)
    
    # Calculate d' (sensitivity) and criterion (c) using z-scores
    z_hit = norm.ppf(hit_rate)
    z_false_alarm = norm.ppf(false_alarm_rate)
    d_prime = z_hit - z_false_alarm
    criterion = - (z_hit + z_false_alarm) / 2
    
    # Store calculated values
    d_prime_values.append(d_prime)
    criterion_values.append(criterion)
    
    # Estimate standard deviations for error bars (using binomial distribution as approximation)
    hit_std = np.sqrt(hit_rate * (1 - hit_rate) / (hits + misses)) if (hits + misses) > 0 else 0
    false_alarm_std = np.sqrt(false_alarm_rate * (1 - false_alarm_rate) / (false_alarms + correct_rejections)) if (false_alarms + correct_rejections) > 0 else 0
    
    # Calculate errors for d' and criterion using error propagation
    d_prime_error = np.sqrt(hit_std**2 + false_alarm_std**2)  # Combined error for d'
    criterion_error = np.sqrt(hit_std**2 + false_alarm_std**2) / 2  # Combined error for criterion
    
    d_prime_errors.append(d_prime_error)
    criterion_errors.append(criterion_error)

# Fit a linear model (degree 1 polynomial) for d' and criterion values
# Linear trend fitting to provide a smooth trend line
d_prime_linear = Polynomial.fit(sorted_set_sizes, d_prime_values, 1)
criterion_linear = Polynomial.fit(sorted_set_sizes, criterion_values, 1)

# Generate smooth x-values to plot the trend lines
smooth_set_sizes = np.linspace(min(sorted_set_sizes), max(sorted_set_sizes), 100)
d_prime_trend_linear = d_prime_linear(smooth_set_sizes)
criterion_trend_linear = criterion_linear(smooth_set_sizes)

# Begin plotting both d' and criterion values with linear trend lines
plt.figure(figsize=(12, 5))

# Plot for d' values with error bars and linear trend line
plt.subplot(1, 2, 1)
plt.errorbar(sorted_set_sizes, d_prime_values, yerr=d_prime_errors, fmt='o', color='b', 
             ecolor='lightblue', elinewidth=2, capsize=4, label="Observed d'")
plt.plot(smooth_set_sizes, d_prime_trend_linear, color='blue', linestyle='--', label="Linear Trend")
plt.xlabel('Set Size')
plt.ylabel("d' (Sensitivity)")
plt.title("d' with Linear Trend for Different Set Sizes")
plt.legend()
plt.grid(True)

# Plot for criterion (c) values with error bars and linear trend line
plt.subplot(1, 2, 2)
#plt.errorbar(sorted_set_sizes, criterion_values, yerr=criterion_errors, fmt='o', color='r', 
#             ecolor='salmon', elinewidth=2, capsize=4, label="Observed Criterion (c)")
plt.plot(smooth_set_sizes, criterion_trend_linear, color='red', linestyle='--', label="Linear Trend")
plt.xlabel('Set Size')
plt.ylabel('Criterion (c)')
plt.title('Criterion with Linear Trend for Different Set Sizes')
plt.legend()
plt.grid(True)

# Display both plots with proper layout
plt.tight_layout()
plt.show()