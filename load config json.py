import json

def load_shift_schedule():
    with open("shift_schedule.json", "r") as json_file:
        data = json.load(json_file)
    return data

def display_available_shifts(shift_schedule):
    print("Available Shifts:")
    for shift in shift_schedule["shifts"]:
        print(f"- {shift}")

def display_timings_for_shift(shift_schedule, selected_shift):
    timings = shift_schedule["shifts"].get(selected_shift)
    if timings:
        print(f"Available Timings for {selected_shift}:")
        for timing in timings:
            print(f"- {timing}")
        return timings
    else:
        print("Invalid shift selected.")
        return None

def display_available_seats(shift_schedule):
    print("Available Seats:")
    seats = shift_schedule["seats"]
    print(", ".join(seats))
    return seats

def main():
    # Load the shift schedule from the JSON file
    shift_schedule = load_shift_schedule()
    
    # Display available shifts
    display_available_shifts(shift_schedule)
    
    # Ask the user to select a shift
    selected_shift = input("\nEnter the shift you want to choose: ").strip()
    
    # Display timings for the selected shift
    timings = display_timings_for_shift(shift_schedule, selected_shift)
    
    if timings:
        # Ask the user to select a timing
        selected_timing = input("\nEnter the timing you want to choose: ").strip()
        
        if selected_timing in timings:
            # Display available seats
            display_available_seats(shift_schedule)
        else:
            print("Invalid timing selected.")
    else:
        print("No timings available for the selected shift.")

if __name__ == "__main__":
    main()
