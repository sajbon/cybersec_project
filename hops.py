import os
import pandas as pd
import subprocess
import re


class Hops:
    def __init__(self):
        self.link = "google.com"

    def hops_revealer(self):
        
        result = subprocess.run(['traceroute', self.link], capture_output=True, text=True)
        for i in result:
            print(result)
