from datetime import datetime, timedelta

# Current date and time
now = datetime.now()
print("Current date and time:", now)

# Add 5 days
future_date = now + timedelta(days=5)
print("After 5 days:", future_date)

# Format date
formatted = now.strftime("%Y-%m-%d")
print("Formatted date:", formatted)