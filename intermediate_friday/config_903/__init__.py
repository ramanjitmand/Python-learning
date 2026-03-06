# From enum module import Enum class (a list, a dictionary, and a df are all types of classes)
from enum import Enum

# For classes you need to use capitals 
# Let's make a new class - indented bits underneath will be part of that class
class DateCols903(Enum):
    # Put columns which are dates here
    cols = [
        "DOB",
        "DATE_INT",
        "DATE_MATCH",
        "DECOM",
        "DEC",
        "MC_DOB",
        "MIS_START",
        "MIS_END",
        "DATE_PLACED",
        "DATE_PLACED_CEASED",
        "DATE_PERM",
        "REVIEW",
        "DUC",
    ]  
# Now go back to utils

class EthnicSubcategories(Enum):
    WBRI = "White"
    WIRI = "White"
    WIRT = "White"
    WROM = "White"
    WOTH = "White"
    MWBC = "Mixed"
    MWBA = "Mixed"
    MWAS = "Mixed"
    MOTH = "Mixed"
    AIND = "Asian"
    APKN = "Asian"
    ABAN = "Asian"
    AOTH = "Asian"
    BCRB = "Black"
    BAFR = "Black"
    BOTH = "Black"
    CHNE = "Chinese"
    OOTH = "Other"
    REFU = "Refused"
    NOBT = "Not Obtained"