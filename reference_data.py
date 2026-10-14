"""Static reference data for PPAScout."""

STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
    "FCT (Abuja)", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
    "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo",
    "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
]

SECTORS = {
    "education": "Education (school/college)",
    "health": "Health",
    "agriculture": "Agriculture",
    "government": "Government / Ministry / Parastatal",
    "private_corporate": "Private / Corporate",
    "banking_finance": "Banking / Finance",
    "tech": "Tech / IT",
    "ngo": "NGO / Non-profit",
    "media": "Media",
    "other": "Other",
}

# NYSC service years, recent + a little future-proofing. "Batch A/B/C" within
# a service year isn't tracked separately here — kept simple.
SERVICE_YEARS = [
    "2026/2027", "2025/2026", "2024/2025", "2023/2024", "2022/2023", "Earlier",
]
