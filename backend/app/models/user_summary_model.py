from datetime import datetime

class UserSummary:
    user_id: str            # UUID stored in user's localStorage
    domain_id: str          # Which business they were chatting with
    summary: str            # AI-generated summary of past conversations
    last_seen: datetime     # When they last visited
    session_count: int      # How many times they've chatted
