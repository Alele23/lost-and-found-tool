export type Category =
  | "Electronics"
  | "Clothing"
  | "Documents"
  | "Jewelry"
  | "Wallet / ID / Cards"
  | "Keys"
  | "Eyewear"
  | "Accessories"
  | "Other"

export const CATEGORIES: Category[] = [
  "Electronics",
  "Clothing",
  "Documents",
  "Jewelry",
  "Wallet / ID / Cards",
  "Keys",
  "Eyewear",
  "Accessories",
  "Other",
]

export type Status = "Found" | "Claimed" | "Lost"

export const STATUSES: Status[] = ["Found", "Claimed", "Lost"]

export interface ItemFields {
  item_description: string
  category: Category
  date_found: string
  location: string
  status: Status
  reported_by: string
  claimed_by: string
  contact: string
  remarks: string
}
