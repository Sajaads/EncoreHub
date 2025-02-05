import datetime
from django.utils.deprecation import MiddlewareMixin
from encorehub.settings import VISITS_COLLECTION

class TrackVisitsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """Track and store daily visits in MongoDB."""
        
        # Get today's date in YYYY-MM-DD format
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Check if there's already an entry for today
        visit_entry = VISITS_COLLECTION.find_one({"date": today})

        if visit_entry:
            # Increment visit count
            VISITS_COLLECTION.update_one(
                {"date": today}, {"$inc": {"count": 1}}
            )
        else:
            # Create new entry
            VISITS_COLLECTION.insert_one({"date": today, "count": 1})

        return None  # Continue with the request
