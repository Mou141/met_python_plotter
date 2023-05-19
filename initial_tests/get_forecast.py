import requests

def get_site_list(key):
    r = requests.get(r"http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist", params={"key": key})
    r.raise_for_status()
    return r.json()