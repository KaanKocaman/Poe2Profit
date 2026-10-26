import os

# Contact info sent in the User-Agent header (GGG asks API clients to include one).
# Set POE2PROFIT_CONTACT to use your own email instead of the repo link.
CONTACT = os.environ.get("POE2PROFIT_CONTACT", "https://github.com/KaanKocaman/Poe2Profit")
USER_AGENT = f"Poe2Profit/1.0 (contact: {CONTACT})"
