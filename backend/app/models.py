from datetime import date
from enum import Enum
from pydantic import BaseModel, Field

class Category(str, Enum):
    ELECTRONICS = "Electronics"
    CLOTHING = "Clothing"
    DOCUMENTS = "Documents"
    JEWELRY = "Jewelry"
    WALLET_ID = "Wallet / ID / Cards"
    KEYS = "Keys"
    EYEWEAR = "Eyewear"
    ACCESSORIES = "Accessories"
    OTHER = "Other"

class Status(str, Enum):
    FOUND = "Found"
    CLAIMED = "Claimed"
    LOST = "Lost"

# Fields Gemini extracts from input photo
class ItemExtraction(BaseModel):
    item_description: str = Field(min_length=1, max_length=300)
    category: Category

class ItemFields(ItemExtraction):
    date_found: date = Field(default_factory=date.today)
    location: str = "Brodhead"
    status: Status = Status.FOUND
    reported_by: str = ""
    claimed_by: str = ""
    contact: str = ""
    remarks: str = ""
