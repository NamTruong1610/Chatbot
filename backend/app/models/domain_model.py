from datetime import datetime

# What a Domain document/record looks like in the database
class Domain:
    domain_id: str          # "catering-xyz"  ← comes from script tag data-domain
    business_name: str      # "XYZ Catering Co."
    welcome_message: str    # "Hi! I can help you book catering. What's the occasion?"
    bot_persona: str        # "You are a helpful assistant for XYZ Catering..."
    allowed_origins: list   # ["https://xyzcatering.com.au"]
    created_at: datetime
    is_active: bool
