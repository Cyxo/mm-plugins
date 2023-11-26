import os
import sys


DIR = os.path.dirname(__file__)

async def setup(bot):
    os.system(f"{sys.executable} -m pip install -r {os.path.join(DIR, '../../../..', 'requirements.txt')}")
