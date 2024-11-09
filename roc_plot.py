import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Load your experiment data
data_file_path = 'kalyanbrata_data.csv'  # Replace with your file path
experiment_data = pd.read_csv(data_file_path)

# Sort set sizes in ascending order for ordered plotting
sorted_set_sizes = sorted(experiment_data['Set Size'].unique())

# Initialize the plot for ROC curves
plt.figure(figsize=(10, 7))

# Loop through each set size in sorted order to calculate d' and plot an ideal ROC curve
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
    
    # To prevent extreme rates from producing undefined z-scores:
    # Adjust hit rate and false alarm rate if they are exactly 0 or 1.
    hit_rate = np.clip(hit_rate, 0.01, 0.99)
    false_alarm_rate = np.clip(false_alarm_rate, 0.01, 0.99)
    
    # Calculate d' value for this set size
    d_prime = norm.ppf(hit_rate) - norm.ppf(false_alarm_rate)
    
    # Generate an idealized ROC curve based on d'
    # We use a range of false alarm rates from 0 to 1 to simulate an ideal ROC
    ideal_false_alarm_rates = np.linspace(0, 1, 100)
    ideal_hit_rates = norm.cdf(norm.ppf(ideal_false_alarm_rates) + d_prime)
    
    # Clip any NaN values or values outside [0, 1] for ideal_hit_rates to keep the ROC plot valid
    ideal_hit_rates = np.clip(ideal_hit_rates, 0, 1)
    
    # Plot the ideal ROC curve for this set size
    plt.plot(ideal_false_alarm_rates, ideal_hit_rates, label=f'Set Size {set_size} (d\' = {d_prime:.2f})')

# Plot formatting and labeling
plt.xlabel('False Alarm Rate')
plt.ylabel('Hit Rate')
plt.title('Idealized ROC Curves for Different Set Sizes')
plt.legend(loc='lower right')
plt.grid(True)
plt.show()