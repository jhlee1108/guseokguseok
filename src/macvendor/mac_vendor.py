import requests

class MacVendor:
    def __init__(self):
        self.url = 'https://api.macvendors.com/'

    def find_vendor(self, mac):
        response = requests.get(self.url + str(mac))
        return response.text 
