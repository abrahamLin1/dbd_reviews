import sys
import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

APP_ID = 381210
API_URL = f"https://store.steampowered.com/appreviews/{APP_ID}"

def fetch_negative_reviews(max_reviews=50):
    reviews = []
    cursor = "*"

    while len(reviews) < max_reviews:
        params = {
            "json": 1,
            "filter": "recent",
            "language": "english",
            "review_type": "negative",
            "num_per_page": min(100, max_reviews - len(reviews)),
            "cursor": cursor,
            "purchase_type": "all",
        }

        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("success") != 1:
            print("API returned an error.")
            break

        batch = data.get("reviews", [])
        if not batch:
            break

        reviews.extend(batch)

        next_cursor = data.get("cursor")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor

    return reviews


def print_review(review, index):
    author = review["author"]["steamid"]
    hours = review["author"]["playtime_forever"] / 60
    voted_up = review.get("voted_up", False)
    text = review.get("review", "").strip()
    votes_helpful = review.get("votes_helpful", 0)

    sentiment = "POSITIVE" if voted_up else "NEGATIVE"
    # print(f"--- Review #{index} ---")
    # print(f"Author SteamID : {author}")
    print(f"Hours played   : {hours:.1f}h")
    # print(f"Sentiment      : {sentiment}")
    # print(f"Helpful votes  : {votes_helpful}")
    print(f"Review         : {text[:500]}{'...' if len(text) > 500 else ''}")
    print()


def main():
    print(f"Fetching negative reviews for Dead by Daylight (App {APP_ID})...\n")
    reviews = fetch_negative_reviews(max_reviews=10)
    print(f"Fetched {len(reviews)} reviews.\n")

    for i, review in enumerate(reviews, start=1):
        print_review(review, i)


if __name__ == "__main__":
    main()
