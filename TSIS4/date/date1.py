from datetime import datetime, timedelta


current_date_time = datetime.now()


result_date = current_date_time - timedelta(days=5)


print("five days ago:", result_date)
