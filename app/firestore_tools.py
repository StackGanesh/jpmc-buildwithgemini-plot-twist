# app/firestore_tools.py
import datetime
import json
from google.cloud import firestore

# CRITICAL: Hardcode GCP Project ID as a string.
# On Agent Platform, google.auth.default() returns project number, breaking Firestore.
PROJECT_ID = "qwiklabs-gcp-02-41b7e175b609"
COLLECTION_NAME = "watchlist"

# Initialize Firestore client with explicit project ID
db = firestore.Client(project=PROJECT_ID)


def add_to_watchlist(
    title: str,
    media_type: str,
    genre: str = "",
    status: str = "want_to_watch",
    rating: float = 0.0,
    notes: str = "",
) -> str:
    """Adds a new book or movie item to the user's PlotTwist watchlist in Firestore.

    Args:
        title: The title of the book or movie.
        media_type: Type of media, either 'book' or 'movie'.
        genre: Genre of the media (e.g. 'Sci-Fi', 'Drama', 'Thriller').
        status: Progress status: 'want_to_watch', 'watching', or 'completed'.
        rating: Optional rating score from 0.0 to 5.0.
        notes: Personal thoughts, recommendations, or content notes.

    Returns:
        A success message with the created item's unique Firestore document ID.
    """
    try:
        doc_ref = db.collection(COLLECTION_NAME).document()
        item_data = {
            "title": title,
            "media_type": media_type.lower(),
            "genre": genre,
            "status": status.lower(),
            "rating": float(rating) if rating else 0.0,
            "notes": notes,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        doc_ref.set(item_data)
        return f"Successfully added '{title}' ({media_type}) to watchlist with ID: {doc_ref.id}"
    except Exception as e:
        return f"Error adding item to watchlist: {str(e)}"


def get_watchlist(media_type: str = "", status: str = "") -> str:
    """Retrieves items from the user's PlotTwist watchlist in Firestore with optional filters.

    Args:
        media_type: Optional filter by 'book' or 'movie'. Leave empty for all media types.
        status: Optional filter by 'want_to_watch', 'watching', or 'completed'. Leave empty for all statuses.

    Returns:
        A JSON string containing the list of watchlist items with item_id, title, media_type, genre, status, rating, and notes.
    """
    try:
        query = db.collection(COLLECTION_NAME)
        if media_type:
            query = query.where("media_type", "==", media_type.lower())
        if status:
            query = query.where("status", "==", status.lower())

        docs = query.stream()
        results = []
        for doc in docs:
            item = doc.to_dict()
            item["item_id"] = doc.id
            results.append(item)

        if not results:
            return "No watchlist items found matching the specified criteria."

        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error retrieving watchlist: {str(e)}"


def update_watchlist_item(
    item_id: str,
    status: str = "",
    rating: float = 0.0,
    notes: str = "",
) -> str:
    """Updates an existing item's status, rating, or notes in the user's PlotTwist watchlist.

    Args:
        item_id: The unique Firestore document ID of the watchlist item.
        status: Updated status ('want_to_watch', 'watching', 'completed'). Pass empty string to keep unchanged.
        rating: Updated rating (0.0 to 5.0). Pass 0.0 to keep unchanged.
        notes: Updated notes or comments. Pass empty string to keep unchanged.

    Returns:
        A confirmation message indicating what fields were updated.
    """
    try:
        doc_ref = doc_ref = db.collection(COLLECTION_NAME).document(item_id)
        doc = doc_ref.get()
        if not doc.exists:
            return f"No watchlist item found with ID: {item_id}"

        updates = {}
        if status:
            updates["status"] = status.lower()
        if rating > 0.0:
            updates["rating"] = float(rating)
        if notes:
            updates["notes"] = notes
        if "updated_at" not in updates:
            updates["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if updates:
            doc_ref.update(updates)
            return f"Successfully updated item '{item_id}' with fields: {list(updates.keys())}"
        else:
            return "No fields provided to update."
    except Exception as e:
        return f"Error updating watchlist item: {str(e)}"
