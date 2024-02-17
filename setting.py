SEARCH_KEY = ""
SEARCH_ID = ""
COUNTRY = "IN"  # Country code for India

SEARCH_URL = f"https://www.googleapis.com/customsearch/v1?key={SEARCH_KEY}&cx={SEARCH_ID}&q={{query}}&start={{start}}&num=10&gl={COUNTRY}"
RESULT_COUNT = 20

import os
if os.path.exists("private.py"):
    from private import SEARCH_KEY, SEARCH_ID


