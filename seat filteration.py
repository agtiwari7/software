import sqlite3
import json
from datetime import datetime, timedelta

# Load JSON data from file
def load_json_data():
    with open('shift_schedule.json', 'r') as json_file:
        data = json.load(json_file)
    return data

# Convert time to 24-hour format with leading zeros
def convert_to_24hr_format(time_str):
    return datetime.strptime(time_str, '%I:%M %p').strftime('%I:%M %p')

# Step 1: Database Connection and Table Creation
def create_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # Create students table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            shift TEXT,
            time_range TEXT,
            seat TEXT
        )
    ''')
    
    conn.commit()
    return conn, cursor

# Step 2: Insert New Student Data into Database
def insert_student(conn, cursor, name, shift, time_range, seat):
    print(name, shift, time_range, seat)
    cursor.execute('''
        INSERT INTO students (name, shift, time_range, seat)
        VALUES (?, ?, ?, ?)
    ''', (name, shift, time_range, seat))
    
    conn.commit()

# Step 3: Conflict Checking Function
def has_conflict(existing_range, new_start, new_end):
    existing_start, existing_end = existing_range.split(" - ")
    # print(existing_start, existing_end, new_start, new_end)
    try:
        existing_start = datetime.strptime(existing_start.strip(), '%I:%M %p')
        existing_end = datetime.strptime(existing_end.strip(), '%I:%M %p')
        new_start = datetime.strptime(new_start.strip(), '%I:%M %p')
        new_end = datetime.strptime(new_end.strip(), '%I:%M %p')
        # print(existing_start, existing_end, new_start, new_end)
    except ValueError:
        print("Error in time format")
        return False

    # Adjust for overnight shifts
    if existing_end <= existing_start:
        existing_end += timedelta(days=1)
    if new_end <= new_start:
        new_end += timedelta(days=1)

    # Overlap detection
    return not (new_end <= existing_start or new_start >= existing_end)

# Step 4: Fetch Available Seats
def get_available_seats(cursor, new_start, new_end, seats):
    available_seats = seats.copy()

    cursor.execute("SELECT seat, time_range FROM students")
    reserved_seats = cursor.fetchall()

    for seat, existing_range in reserved_seats:
        if has_conflict(existing_range, new_start, new_end):
            if seat in available_seats:
                available_seats.remove(seat)

    return available_seats

# Function to get valid time input
def get_time_input(prompt):
    while True:
        time_input = input(prompt)
        try:
            datetime.strptime(time_input, '%I:%M %p')
            return time_input
        except ValueError:
            print("Invalid time format. Please enter time in 'HH:MM AM/PM' format.")

# Main Function
def main():
    # Load shift and seat data from JSON file
    data = load_json_data()
    shifts = data["shifts"]
    seats = data["seats"]

    conn, cursor = create_db()

    # Display shift options
    print("Available shifts:")
    for shift in shifts:
        print(shift)
    
    selected_shift = input("Shift (e.g., 6 hrs, 12 hrs): ").strip()
    if selected_shift not in shifts:
        print("Invalid shift selected.")
        return

    # Display timing options for selected shift
    print(f"Available timings for {selected_shift}:")
    for timing in shifts[selected_shift]:
        print(timing)

    selected_timing = input(f"Please enter the timing (e.g., 6 AM - 12 PM) for the {selected_shift} shift: ").strip()
    
    if selected_timing not in shifts[selected_shift]:
        print("Invalid timing selected.")
        return

    # Extract start and end times from the selected timing
    try:
        new_student_start, new_student_end = selected_timing.split(" - ")
        # Convert to 24-hour format with leading zeros
        # new_student_start = convert_to_24hr_format(new_student_start)
        # new_student_end = convert_to_24hr_format(new_student_end)
        time_range = f"{new_student_start} - {new_student_end}"
        available_seats = get_available_seats(cursor, new_student_start, new_student_end, seats)

        if available_seats:
            print(f"Available seats for the new student: {', '.join(available_seats)}")

            chosen_seat = input("Please enter the seat number to allocate (e.g., s3): ")

            if chosen_seat in available_seats:
                insert_student(conn, cursor, 'bob', selected_shift, time_range, chosen_seat)
                print(f"Seat {chosen_seat} allocated to the new student.")
            else:
                print("The seat you selected is not available.")
        else:
            print("No available seats for this timing.")
    except ValueError:
        print("Invalid timing format. Make sure to use 'HH:MM AM/PM - HH:MM AM/PM' format.")

    conn.close()

if __name__ == '__main__':
    main()
