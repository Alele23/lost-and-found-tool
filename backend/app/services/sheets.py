import gspread
from app.config import get_settings

def get_sheet(settings):
    client = gspread.service_account(filename=settings.google_credentials_path)
    spreadsheet = client.open_by_key(settings.sheet_id)
    return spreadsheet.sheet1

# Convert ItemFields into a row because append_row wants a plain list[str] in column order
def to_row(item):
    return [
        item.item_description,
        item.date_found.isoformat(),
        item.category.value,
        item.location,
        item.status.value,
        item.reported_by,
        item.claimed_by,
        item.contact,
        item.remarks,
    ]

def append_item(item, sheet=None, settings=None):
    settings = settings or get_settings()
    sheet = sheet or get_sheet(settings)
    sheet.append_row(to_row(item))