# seed_firestore.py
import datetime
from google.cloud import firestore

# CRITICAL: Hardcode GCP Project ID as a string.
# On Agent Platform, google.auth.default() returns project number, breaking Firestore.
PROJECT_ID = "qwiklabs-gcp-02-41b7e175b609"
COLLECTION_NAME = "watchlist"

SEED_ITEMS = [
    {
        "title": "Interstellar",
        "media_type": "movie",
        "genre": "Sci-Fi",
        "status": "completed",
        "rating": 5.0,
        "notes": "Stunning space epic on time dilation and love across dimensions.",
    },
    {
        "title": "Dune",
        "media_type": "book",
        "genre": "Sci-Fi",
        "status": "watching",  # currently reading
        "rating": 4.5,
        "notes": "Classic science fiction masterpiece by Frank Herbert.",
    },
    {
        "title": "The Dark Knight",
        "media_type": "movie",
        "genre": "Action",
        "status": "completed",
        "rating": 5.0,
        "notes": "Christopher Nolan's iconic superhero crime thriller.",
    },
    {
        "title": "Project Hail Mary",
        "media_type": "book",
        "genre": "Sci-Fi",
        "status": "want_to_watch",
        "rating": 0.0,
        "notes": "Highly recommended sci-fi novel by Andy Weir.",
    },
]


def seed_firestore():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connecting to Firestore for project '{PROJECT_ID}'...")

    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEED_ITEMS:
        # Check if item already exists to avoid duplicate seed entries
        existing = (
            collection_ref.where("title", "==", item["title"])
            .where("media_type", "==", item["media_type"])
            .get()
        )
        if existing:
            print(f"Item '{item['title']}' ({item['media_type']}) already exists in Firestore. Skipping.")
            continue

        doc_ref = collection_ref.document()
        item_data = {
            **item,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        doc_ref.set(item_data)
        print(f"Added seed item: '{item['title']}' ({item['media_type']}) with ID {doc_ref.id}")

    print("Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_firestore()
