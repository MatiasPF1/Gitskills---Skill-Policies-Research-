import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from HelperFunctions.HelperFunctions_Mechanisms.Mechanisms import MECHANISMS, save_found
from HelperFunctions.HelperFunctions_Mechanisms.Architectural_Engineer import save_software


'''
Runs the whole mechanism pipeline, one mechanism at a time in MECHANISMS order (Ask, then Act, then Escalate)
1. save_found --> Mechanisms/Mechanisms_<mechanism>/Found, the TOP skills holding the most keywords of that mechanism
2. save_software --> Mechanisms/SWE_SKILLS/<mechanism>, the ones among them about software architecture or engineering
taken is shared by every mechanism, so a skill saved by an earlier mechanism is never saved again by a later one
'''
taken = set()
for mechanism, keywords in MECHANISMS.items():
    found = save_found(keywords, mechanism, taken)
    swe = save_software(mechanism)
    print(f"{mechanism}: {len(found)} found --> {len(swe)} software skills")
