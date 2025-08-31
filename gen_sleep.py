import random
import datetime
import matplotlib.pyplot as plt


def get_sleep_time(time_of_day):
    """
    Calculate sleep time based on time of day (0.0 to 1.0 representing 24 hours).

    Args:
        time_of_day (float): Time as fraction of day (0.0 = midnight, 0.5 = noon, 1.0 = midnight)

    Returns:
        float: Sleep time in seconds
    """
    # Determine activity level based on time of day
    if random.uniform(22, 23.5) / 24 <= time_of_day or time_of_day <= 6 / 24:
        # Night time (10 PM - 6 AM): Very low activity
        activity_level = random.uniform(0.1, 0.3)
    elif time_of_day <= random.uniform(7, 13) / 24:
        # Morning to early afternoon: Medium activity
        activity_level = random.uniform(0.3, 0.6)
    else:
        # Afternoon to evening: High activity
        activity_level = random.uniform(0.6, 1)

    # Generate base sleep time based on activity level
    if activity_level > 0.75:
        # High activity: short, frequent refreshes
        base_sleep = random.uniform(5, 15)
    elif activity_level > 0.725:
        # High activity: short to medium refreshes
        base_sleep = random.uniform(25, random.uniform(60, 90))
    elif activity_level > 0.6:
        # High activity: very short refreshes
        base_sleep = random.uniform(3, 10)
    elif activity_level > 0.3:
        # Medium activity: moderate refreshes
        base_sleep = random.uniform(20, 90)
    elif activity_level > 0.1:
        # Low activity: longer refreshes
        base_sleep = random.uniform(60, 2 * 60)
    else:
        # Very low activity: longest refreshes
        base_sleep = random.uniform(60, 3 * 60)

    # Add variation
    variation = random.uniform(0.75, 1.25)

    # Occasionally add "burst" activity (rapid refreshes)
    if random.random() < 0.05 and activity_level > 0.5:
        variation *= random.uniform(0.75, 1)

    # Occasionally add "distraction" periods (longer pause during active time)
    if random.random() < 0.05 and activity_level > 0.5:
        variation *= random.uniform(1, 1.25)

    # For now, keeping variation = 1 as in original code
    # variation = 1
    sleep_time = round(base_sleep * variation, 1)

    print(time_fraction_to_datetime(time_of_day), sleep_time, round(activity_level, 2))
    return sleep_time, activity_level


def generate_sleep_times():
    """
    Generate a list of sleep times (in seconds) for 24 hours that mimics human behavior.

    Returns:
        tuple: (sleep_times, activity_levels) - lists for a full day
    """
    sleep_times = []
    activities_level = []
    now = datetime.datetime.now()
    time_of_day = now.second + now.minute * 60 + now.hour * 3600
    time_of_day *= 1
    current_time = time_of_day
    total_seconds = 24 * 60 * 60 + time_of_day

    while current_time < total_seconds:
        # Calculate time of day as fraction (0.0 to 1.0)
        time_of_day = (current_time % (24 * 60 * 60)) / (24 * 60 * 60)

        # Get sleep time and activity level for this time of day
        sleep_time, activity_level = get_sleep_time(time_of_day)

        # Check if adding this sleep time would exceed our 24-hour period
        if current_time + sleep_time >= total_seconds:
            break

        sleep_times.append(sleep_time)
        activities_level.append(activity_level)
        # current_time += sleep_time
        current_time += sleep_time * 60

    return sleep_times, activities_level


def plot_sleep_data(sleep_times, activities_level):
    """
    Plot sleep times and activity levels.

    Args:
        sleep_times (list): List of sleep times
        activities_level (list): List of activity levels
    """
    fig, axs = plt.subplots(2, 1, figsize=(12, 8))

    # Plot sleep times
    axs[0].plot(sleep_times, marker='o', color='blue', linewidth=1, markersize=3)
    axs[0].set_title("Sleep Times Throughout the Day")
    axs[0].set_ylabel("Sleep Time (seconds)")
    axs[0].grid(True, alpha=0.3)

    # Plot activity levels
    axs[1].plot(activities_level, marker='s', color='green', linewidth=1, markersize=3)
    axs[1].set_title("Activity Levels Throughout the Day")
    axs[1].set_xlabel("Time Period")
    axs[1].set_ylabel("Activity Level")
    axs[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def format_sleep_times(sleep_times):
    """Format sleep times for better readability"""
    total_time = sum(sleep_times)
    hours = int(total_time // 60)
    minutes = int(total_time % 60)

    print(f"Total time: {total_time:.1f} seconds")
    print(f"Total refreshes: {len(sleep_times)}")
    print(f"Total time covered: {hours}h {minutes}m")
    print(f"Average sleep time: {sum(sleep_times) / len(sleep_times):.1f} seconds")
    print(f"Min sleep time: {min(sleep_times):.1f} seconds")
    print(f"Max sleep time: {max(sleep_times):.1f} seconds")

    return sleep_times


def time_fraction_to_datetime(fraction, base_date=None):
    """Convert time fraction (0.0-1.0) to datetime"""
    if base_date is None:
        base_date = datetime.date.today()

    seconds = fraction * 24 * 60 * 60
    midnight = datetime.datetime.combine(base_date, datetime.time.min)
    return midnight + datetime.timedelta(seconds=seconds)

# Example usage
if __name__ == "__main__":
    sleep_times, activities_level = generate_sleep_times()
    print(sleep_times)
    format_sleep_times(sleep_times)
    plot_sleep_data(sleep_times, activities_level)
