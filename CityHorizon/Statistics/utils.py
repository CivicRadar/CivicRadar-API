import matplotlib.pyplot as plt
import numpy as np
import os
from django.conf import settings
from datetime import datetime

def generate_and_save_charts(report_id):
    """
    Generate charts and save them to MEDIA_ROOT with unique filenames based on report_id.
    Returns a dictionary of chart filenames for storage in the model.
    """
    chart_files = {}

    # 1. Pie Chart: City Problem Status Distribution
    pie_dir = os.path.join(settings.MEDIA_ROOT, 'charts', 'problem_status')
    os.makedirs(pie_dir, exist_ok=True)  # Ensure subdirectory exists
    statuses = ['PendingReview', 'UnderConsideration', 'IssueResolved']
    status_counts = [30, 40, 30]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    explode = (0.1, 0, 0)

    plt.figure(figsize=(8, 6))
    plt.pie(status_counts, labels=statuses, colors=colors, explode=explode, autopct='%1.1f%%', startangle=90, shadow=True)
    plt.title('City Problem Status Distribution', fontsize=14, pad=20)
    plt.axis('equal')
    pie_file = f'charts/problem_status/problem_status_pie_{report_id}.png'
    plt.savefig(os.path.join(settings.MEDIA_ROOT, pie_file), bbox_inches='tight')
    plt.close()
    chart_files['problem_status_pie_chart'] = pie_file

    # 2. Bar Chart: Problems by Type
    type_dir = os.path.join(settings.MEDIA_ROOT, 'charts', 'problem_type')
    os.makedirs(type_dir, exist_ok=True)  # Ensure subdirectory exists
    problem_types = ['Lighting', 'Garbage', 'Street', 'Other']
    type_counts = [25, 40, 20, 15]
    colors = ['#ffcc99', '#99ccff', '#ccff99', '#ff99cc']

    plt.figure(figsize=(10, 6))
    plt.bar(problem_types, type_counts, color=colors, edgecolor='black')
    plt.title('Problems by Type', fontsize=14)
    plt.xlabel('Problem Type', fontsize=12)
    plt.ylabel('Number of Problems', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    for i, v in enumerate(type_counts):
        plt.text(i, v + 0.5, str(v), ha='center', fontsize=10)
    type_file = f'charts/problem_type/problem_type_bar_{report_id}.png'
    plt.savefig(os.path.join(settings.MEDIA_ROOT, type_file), bbox_inches='tight')
    plt.close()
    chart_files['problem_type_bar_chart'] = type_file

    # 3. Bar Chart: Citizen Engagement (Likes vs Dislikes)
    engagement_dir = os.path.join(settings.MEDIA_ROOT, 'charts', 'engagement')
    os.makedirs(engagement_dir, exist_ok=True)  # Ensure subdirectory exists
    engagement = ['Likes', 'Dislikes']
    engagement_counts = [150, 50]
    colors = ['#66ff66', '#ff6666']

    plt.figure(figsize=(8, 6))
    plt.bar(engagement, engagement_counts, color=colors, edgecolor='black')
    plt.title('Citizen Engagement on City Problems', fontsize=14)
    plt.ylabel('Number of Reactions', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    for i, v in enumerate(engagement_counts):
        plt.text(i, v + 5, str(v), ha='center', fontsize=10)
    engagement_file = f'charts/engagement/engagement_bar_{report_id}.png'
    plt.savefig(os.path.join(settings.MEDIA_ROOT, engagement_file), bbox_inches='tight')
    plt.close()
    chart_files['engagement_bar_chart'] = engagement_file

    # 4. Line Chart: Problems Resolved Over Time
    resolved_dir = os.path.join(settings.MEDIA_ROOT, 'charts', 'resolved_over_time')
    os.makedirs(resolved_dir, exist_ok=True)  # Ensure subdirectory exists
    months = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
              '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12',
              '2025-01', '2025-02', '2025-03', '2025-04']
    resolved_counts = [5, 7, 10, 8, 12, 15, 10, 13, 18, 20, 15, 12, 10, 8, 14, 16]

    plt.figure(figsize=(12, 6))
    plt.plot(months, resolved_counts, marker='o', color='#3366cc', linewidth=2, markersize=8)
    plt.title('Problems Resolved Over Time (Monthly)', fontsize=14)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Number of Problems Resolved', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    for i, v in enumerate(resolved_counts):
        plt.text(i, v + 0.5, str(v), ha='center', fontsize=10)
    plt.tight_layout()
    resolved_file = f'charts/resolved_over_time/resolved_over_time_line_{report_id}.png'
    plt.savefig(os.path.join(settings.MEDIA_ROOT, resolved_file), bbox_inches='tight')
    plt.close()
    chart_files['resolved_over_time_line_chart'] = resolved_file

    # 5. Bar Chart: Average Time to Transition from PendingReview
    transition_dir = os.path.join(settings.MEDIA_ROOT, 'charts', 'transition_time')
    os.makedirs(transition_dir, exist_ok=True)  # Ensure subdirectory exists
    transitions = ['To UnderConsideration', 'To IssueResolved']
    avg_times = {
        'Lighting': [5, 12],
        'Garbage': [7, 15],
        'Street': [10, 20],
        'Other': [8, 18]
    }
    problem_types = ['Lighting', 'Garbage', 'Street', 'Other']
    x = np.arange(len(problem_types))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, [avg_times[ptype][0] for ptype in problem_types], width, label='To UnderConsideration', color='#66b3ff', edgecolor='black')
    plt.bar(x + width/2, [avg_times[ptype][1] for ptype in problem_types], width, label='To IssueResolved', color='#ff9999', edgecolor='black')
    plt.title('Average Time to Transition from PendingReview', fontsize=14)
    plt.xlabel('Problem Type', fontsize=12)
    plt.ylabel('Average Time (Days)', fontsize=12)
    plt.xticks(x, problem_types)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    for i, ptype in enumerate(problem_types):
        plt.text(i - width/2, avg_times[ptype][0] + 0.5, str(avg_times[ptype][0]), ha='center', fontsize=10)
        plt.text(i + width/2, avg_times[ptype][1] + 0.5, str(avg_times[ptype][1]), ha='center', fontsize=10)
    transition_file = f'charts/transition_time/transition_time_bar_{report_id}.png'
    plt.savefig(os.path.join(settings.MEDIA_ROOT, transition_file), bbox_inches='tight')
    plt.close()
    chart_files['transition_time_bar_chart'] = transition_file

    return chart_files