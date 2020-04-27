from ..const.const import (
    MONTH_TO_NUMBER,
    SENSOR_LOCATIONS_TO_URL,
    _LOGGER,
)
from datetime import datetime, date
from bs4 import BeautifulSoup
import urllib.request
import urllib.error


class VenloAfval(object):
    def get_date_from_afvaltype(self, tableRows, afvaltype, afvalnaam):
        try:
            for row in tableRows:
                garbageDate = row.find("td")
                garbageType = row.find("span")
                if garbageDate and garbageType:
                    garbageDate = row.find("td").string
                    garbageType = row.find("span").string

                    #Does the afvaltype match...
                    if garbageType == afvaltype:
                        day = garbageDate.split()[1]
                        month = MONTH_TO_NUMBER[garbageDate.split()[2]]
                        year = str(
                            datetime.today().year
                            if datetime.today().month <= int(month)
                            else datetime.today().year + 1
                        )
                        garbageDate = year + "-" + month + "-" + day

                        if datetime.strptime(garbageDate, '%Y-%m-%d').date() >= date.today():
                            return garbageDate
            # if nothing was found
            return ""
        except Exception as exc:
            _LOGGER.warning("Something went wrong while splitting data: %r. This probably means that trash type %r is not supported on your location", exc, afvalnaam)
            return ""

    def get_data(self, city, postcode, street_number):
        _LOGGER.debug("Updating Waste collection dates")

        try:
            url = SENSOR_LOCATIONS_TO_URL["venlo"][0].format(
                postcode, street_number
            )
            req = urllib.request.Request(url=url)
            f = urllib.request.urlopen(req)
            html = f.read().decode("utf-8")

            soup = BeautifulSoup(html, "html.parser")

            html = soup.find("div", {"class": "trash-removal-calendar"})
            tableRows = html.findAll("tr")

            # Place all possible values in the dictionary even if they are not necessary
            waste_dict = {}
            # GFT
            waste_dict["gft"] = self.get_date_from_afvaltype(tableRows, "GFT", "gft")
            # Restafval
            waste_dict["restafval"] = self.get_date_from_afvaltype(tableRows, "Restafval/PMD", "restafval")
            # PMD
            waste_dict["pbd"] = self.get_date_from_afvaltype(tableRows, "Restafval/PMD", "pbd")

            return waste_dict
        except urllib.error.URLError as exc:
            _LOGGER.error("Error occurred while fetching data: %r", exc.reason)
            return False
