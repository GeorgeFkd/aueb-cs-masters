import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read data from the specified CSV file
df = pd.read_csv('./cmake-build-release/results.csv')

# Calculate the percentage improvement of Incremental over Simple
df['Percentage Improvement'] = ((df['Simple Average Time'] - df['Incremental Average Time']) / df['Simple Average Time']) * 100

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Set the width of each bar
bar_width = 0.35

# Set the position of bars on the x-axis
r1 = np.arange(len(df['Problem Size']))
r2 = [x + bar_width for x in r1]

# Plot bars for Simple Average Time
bars1 = ax.bar(r1, df['Simple Average Time'], color='blue', width=bar_width, edgecolor='grey', label='Simple Average Time')

# Plot bars for Incremental Average Time
bars2 = ax.bar(r2, df['Incremental Average Time'], color='red', width=bar_width, edgecolor='grey', label='Incremental Average Time')

# Labels and title
ax.set_xlabel('Problem Size')
ax.set_ylabel('Time (s)')
ax.set_title('Comparison of Simple vs Incremental Average Time for Different Problem Sizes')

# Set x-ticks at the center of both bars
ax.set_xticks([r + bar_width / 2 for r in range(len(df['Problem Size']))])
ax.set_xticklabels(df['Problem Size'])

# Add legend in the center
ax.legend(loc='upper center')

# Set y-axis to have more readable ticks
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.6g}s'))  # format y-axis ticks
ax.tick_params(axis='y', rotation=0)  # keep y-ticks horizontal for better readability

# Annotate percentage improvement on the bars
for i in range(len(df)):
    ax.annotate(f'{df["Percentage Improvement"].iloc[i]:.2f}%',
                xy=(r1[i] + bar_width / 2, df['Simple Average Time'].iloc[i] + 1),
                ha='center',
                va='bottom')

# Show grid for easier comparison
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show the plot
plt.tight_layout()  # Adjust layout for better spacing
plt.show()
