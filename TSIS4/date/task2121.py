from datetime import datetime, timedelta


currentdate = datetime.now()
newdate = currentdate + timedelta(days=7)
print(newdate)
