import json

def create_shift_schedule():
    shift_schedule = {}
    
    # Enter shift names
    shift_names = input("Enter shift (e.g., 6 hrs, 12 hrs, night): ")
    shift_list = [shift.strip() for shift in shift_names.split(',')]
    for shift_name in shift_list:
        # Enter all timings for this shift in a comma-separated format
        timings = input(f"{shift_name} timings (e.g., 06:00 AM - 12:00 PM, 12:00 PM - 06:00 PM): ")
        timing_list = [timing.strip() for timing in timings.split(',')]
        shift_schedule[shift_name] = timing_list
    

    fees = input("Fees: ")
    fees_list = [fees.strip() for fees in fees.split(',')]

    # Total number of seats
    total_seats = int(input("Total seats: "))
    seats = [f's{i+1}' for i in range(total_seats)]
    # Final structure
    data = {
        "shifts": shift_schedule,
        "fees": fees_list,
        "seats": seats
    }
    
    # Saving to a JSON file with seats in a single line
    with open("shift_schedule.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    print("JSON file 'shift_schedule.json' created successfully!")

# Run the function
create_shift_schedule()
