import time

# List to store events with their timestamps
event_list = []

def log_event(event):
    """Logs an event with the current timestamp."""
    current_time = time.time()
    # Create a dictionary with the event and timestamp
    event_data = {"event": event, "timestamp": current_time}
    if event == "Push audio to stream":
        last_event = event_list[-1] if event_list else None
        if last_event:
            if last_event["event"] == event:
                event_list[-1] = event_data
            else:
                event_list.append(event_data)
    else:
        event_list.append(event_data)

def get_all_events():
    """Displays the events with time elapsed between consecutive events."""
    result = []
    for i in range(1, len(event_list)):
        # Calculate the time elapsed between nth and (n-1)th events
        elapsed_time = event_list[i]["timestamp"] - event_list[i - 1]["timestamp"]
        # Format the output message
        result.append(
            f"Time between event {i} ('{event_list[i-1]['event']}') and event {i+1} ('{event_list[i]['event']}'): {elapsed_time:.1f} seconds"
        )
    return "\n".join(result)