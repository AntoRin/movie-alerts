from services.BookingDataHandler import BookingDataHandler
from services.GUI import GUI, App 

app = App(data_service=BookingDataHandler())
app.mainloop()
# gui = GUI(BookingDataHandler())


