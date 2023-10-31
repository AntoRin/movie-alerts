import customtkinter as ctk
from tkinter import ttk, messagebox
from .BookingDataHandler import BookingDataHandler


class App(ctk.CTk):
    def __init__(self, data_service: BookingDataHandler, *args, **kwargs) -> None:
        ctk.set_appearance_mode("dark")
        super().__init__(*args, **kwargs)

        self.data_service = data_service
        self.app_state = {
            "selected_region": None,
            "all_citites": None
        }

        self.geometry("800x600")
        self.title("BMS Alerts")

        self.venue_selection_frame = self.create_venue_selection_frame()
        self.movie_selection_frame = self.create_movie_selection_frame()

        self.venue_selection_frame.pack(padx="10", pady="10", fill="x")

    def create_venue_selection_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self, corner_radius=10)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=2)

        regions = self.data_service.get_regions()
        top_cities, other_cities = regions["BookMyShow"]["TopCities"], regions["BookMyShow"]["OtherCities"]

        self.app_state["all_cities"] = top_cities + other_cities

        ctk.CTkLabel(frame, text="Select a City", font=("Roboto", 16)).grid(
            column=0, row=0, sticky=ctk.W, padx=10, pady=10)

        ctk.CTkOptionMenu(master=frame, command=self.get_cinemas_for_region, values=list(
            map(lambda x: x["RegionName"], self.app_state["all_cities"]))).grid(column=1, row=0, sticky=ctk.E, padx=10, pady=10)
        return frame

    def create_movie_selection_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self)
        return frame

    def get_cinemas_for_region(self, value):
        for region in self.app_state["all_cities"]:
            if region["RegionName"] == value:
                self.app_state["selected_region"] = region
                break

        venue_data = self.data_service.get_cinemas(region_code=self.app_state["selected_region"]["RegionCode"], region_text=self.app_state[
                                                "selected_region"]["RegionName"], region_slug=self.app_state["selected_region"]["RegionSlug"])

        self.app_state["venues"] = venue_data["cinemas"]["BookMyShow"]["aiVN"]["venues"]
        
                


class GUI:
    def __init__(self, data_service: BookingDataHandler) -> None:
        self.data_service = data_service
        self.data_service.get_regions()

        self.movies_list_dropdown = None
        self.movie_timing_list_dropdown = None

        self.window = tk.Tk()
        self.setup_window_config()
        self.setup_form_elements()
        self.window.mainloop()

    def setup_window_config(self):
        self.window.geometry("800x600")
        self.window.title("BMS Alerts")

    def setup_form_elements(self):
        tk.Label(text="Enter Cinema URL").pack(fill="x")

        url_input_element = tk.Entry()
        url_input_element.insert(
            0, "https://in.bookmyshow.com/buytickets/srk-miraj-cinemas-coimbatore/cinema-coim-SRMJ-MT/20221211")
        url_input_element.pack(fill="x", padx=20, pady=20)
        url_input_element.focus_set()

        tk.Button(text="Search", command=self.__bind__(
            self.handle_movie_query, url_input_element)).pack(fill="x")

    def __bind__(self, function, arg):
        def x(): return function(arg)
        return x

    def handle_movie_query(self, url_input_element):
        try:
            cinema_url = url_input_element.get()
            print(cinema_url)

            available_show_dates, show_details = self.data_service.handle_query({
                "cinema_url": cinema_url
            })

            if not len(show_details):
                raise Exception("NO_SHOW_FOR_DATE")

            self.show_details = show_details

            movies = show_details[0]["Event"]

            default_dropdown_value = tk.StringVar()
            default_dropdown_value.set("Select a movie")

            if self.movies_list_dropdown:
                self.movies_list_dropdown.pack_forget()

            self.movies_list_dropdown = tk.OptionMenu(
                self.window, default_dropdown_value, command=self.handle_movie_selection, *list(map(lambda Event: Event["EventTitle"], movies)))

            self.movies_list_dropdown.pack()
        except Exception as e:
            error_message, = e.args
            if error_message == "NO_SHOW_FOR_DATE":
                messagebox.showinfo(title="", message="No show for date")
            elif error_message == "CONN_ERR":
                messagebox.showerror(
                    title="", message="There was a connection error; make sure you provide the correct URL")
            else:
                messagebox.showerror(
                    title="There was an unexpected error", message=error_message)

    def handle_movie_selection(self, value):
        print(value)
        if not self.show_details:
            raise Exception("No show details found")

        movies = self.show_details[0]["Event"]
        selected_movie = None

        for movie in movies:
            if movie["EventTitle"] == value:
                selected_movie = movie
                break

        if not selected_movie:
            raise Exception("Selected movie not found")

        default_dropdown_value = tk.StringVar()
        default_dropdown_value.set("Select show timing")

        if self.movie_timing_list_dropdown:
            self.movie_timing_list_dropdown.pack_forget()

        def handle_timing_selection(value):

            pass

        self.movie_timing_list_dropdown = tk.OptionMenu(self.window, default_dropdown_value, command=self.handle_timing_selection,
                                                        *list(map(lambda x: x["ShowTime"], selected_movie["ChildEvents"][0]["ShowTimes"])))
        self.movie_timing_list_dropdown.pack()
