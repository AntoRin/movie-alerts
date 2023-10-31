import json
import requests


class BookingDataHandler:
    def __init__(self) -> None:
        self.request_headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
        }

    def handle_query(self, options: dict):
        cinema_url = options.get("cinema_url")
        movie_name = options.get("movie_name")
        show_time = options.get("show_time")

        return self.get_movie_data(cinema_url=cinema_url)

    def get_regions(self):
        res = requests.get(
            "https://in.bookmyshow.com/api/explore/v1/discover/regions", headers=self.request_headers)
        res_json = res.json()
        return res_json
        
    def get_cinemas(self, region_code, region_text, region_slug):
        res = requests.get("https://in.bookmyshow.com/serv/getData?cmd=QUICKBOOK&type=MT&getRecommendedData=1&_=1671333019349&regionCode=ZIRO", headers={
            **self.request_headers,
            "Referer": "https://in.bookmyshow.com/coimbatore/cinemas"
        }, cookies={
            "Rgn": f"%7CCode%3D{region_code}%7Ctext%3D{region_text}%7Cslug%3D{region_slug}%7C"
        })
        res_json = res.json()
        return res_json

    def get_movie_data(self, cinema_url):
        try:
            movie_res = requests.get(
                cinema_url, headers=self.request_headers, allow_redirects=True, timeout=3)

            html = movie_res.text

            if not movie_res.ok:
                raise Exception(html)

            if "text/html" not in movie_res.headers["content-type"]:
                raise Exception("Expected HTML response")

            data_json_string = html[html.index("\"{", html.index(
                "UAPI")): html.index("\")", html.index("UAPI")) + 1]

            data_dict = json.loads(data_json_string)

            if isinstance(data_dict, str):
                data_dict = json.loads(data_dict)

            available_show_dates = data_dict["ShowDatesArray"]
            show_details = data_dict["ShowDetails"]

            return available_show_dates, show_details
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.ConnectionError):
                raise Exception("CONN_ERR")
        except Exception as e:
            raise e
