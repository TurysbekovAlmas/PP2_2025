from datetime import datetime


today = datetime.now()
withoutmicr = today.replace(microsecond=0)


print(withoutmicr)
