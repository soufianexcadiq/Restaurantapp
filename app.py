from datetime import datetime

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

RESTAURANT = {
    "name": "Atlas Table",
    "tagline": "Modern Moroccan dining with a fresh city pulse.",
    "hours": {
        "Monday": "Closed",
        "Tuesday": "12:00 - 22:30",
        "Wednesday": "12:00 - 22:30",
        "Thursday": "12:00 - 22:30",
        "Friday": "12:00 - 23:30",
        "Saturday": "11:00 - 23:30",
        "Sunday": "11:00 - 21:30",
    },
    "phone": "+212-724011310",
    "address": "14 Rue de la Corniche, Casablanca",
}

MENU = [
    {
        "category": "Starters",
        "items": [
            {
                "name": "Zaalouk Crostini",
                "description": "Charred eggplant, preserved lemon, cumin oil, crisp bread.",
                "price": "55 MAD",
                "tags": ["vegetarian"],
                "diet": ["vegetarian"],
                "moods": ["light", "sharing", "classic"],
                "spice": 2,
                "calories": 320,
                "allergens": ["gluten"],
                "image": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=900&q=80",
                "image_alt": "A colorful vegetable appetizer served with crisp bread.",
            },
            {
                "name": "Harira Veloute",
                "description": "Silky tomato-lentil soup, herbs, dates, lemon foam.",
                "price": "48 MAD",
                "tags": ["signature"],
                "diet": ["vegetarian"],
                "moods": ["cozy", "classic", "light"],
                "spice": 1,
                "calories": 260,
                "allergens": [],
                "image": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80",
                "image_alt": "A warm bowl of tomato and lentil soup with herbs.",
            },
            {
                "name": "Saffron Calamari",
                "description": "Tender calamari, chermoula aioli, smoked paprika.",
                "price": "72 MAD",
                "tags": ["seafood"],
                "diet": ["seafood"],
                "moods": ["sharing", "bold", "coastal"],
                "spice": 3,
                "calories": 410,
                "allergens": ["shellfish", "gluten"],
                "image": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?auto=format&fit=crop&w=900&q=80",
                "image_alt": "Golden fried calamari served with a creamy dipping sauce.",
            },
        ],
    },
    {
        "category": "Mains",
        "items": [
            {
                "name": "Citrus Chicken Tagine",
                "description": "Free-range chicken, olives, candied lemon, almond couscous.",
                "price": "135 MAD",
                "tags": ["popular"],
                "diet": ["meat"],
                "moods": ["classic", "cozy", "bold"],
                "spice": 2,
                "calories": 690,
                "allergens": ["nuts"],
                "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=900&q=80",
                "image_alt": "A fragrant chicken dish served with rice and herbs.",
            },
            {
                "name": "Atlantic Sea Bass",
                "description": "Grilled sea bass, herb salad, roasted peppers, lemon butter.",
                "price": "168 MAD",
                "tags": ["seafood"],
                "diet": ["seafood", "light"],
                "moods": ["coastal", "light", "date night"],
                "spice": 1,
                "calories": 540,
                "allergens": ["fish", "dairy"],
                "image": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=900&q=80",
                "image_alt": "Grilled fish with lemon, herbs, and vegetables.",
            },
            {
                "name": "Seven-Vegetable Couscous",
                "description": "Seasonal vegetables, caramelized onion, chickpeas, tfaya jus.",
                "price": "118 MAD",
                "tags": ["vegetarian"],
                "diet": ["vegetarian"],
                "moods": ["cozy", "classic", "healthy"],
                "spice": 1,
                "calories": 590,
                "allergens": ["gluten"],
                "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=80",
                "image_alt": "A bright vegetable couscous-style plate with chickpeas and greens.",
            },
        ],
    },
    {
        "category": "Desserts",
        "items": [
            {
                "name": "Orange Blossom Panna Cotta",
                "description": "Cream, citrus gel, toasted pistachio, mint.",
                "price": "58 MAD",
                "tags": ["fresh"],
                "diet": ["vegetarian"],
                "moods": ["light", "sweet", "date night"],
                "spice": 0,
                "calories": 310,
                "allergens": ["dairy", "nuts"],
                "image": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=900&q=80",
                "image_alt": "A creamy panna cotta dessert topped with fruit and mint.",
            },
            {
                "name": "Date Fondant",
                "description": "Warm date cake, salted caramel, vanilla ice cream.",
                "price": "64 MAD",
                "tags": ["chef pick"],
                "diet": ["vegetarian"],
                "moods": ["sweet", "cozy", "bold"],
                "spice": 0,
                "calories": 470,
                "allergens": ["dairy", "gluten"],
                "image": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=900&q=80",
                "image_alt": "A warm cake dessert served with ice cream and caramel.",
            },
        ],
    },
]

RESERVATIONS = []


def all_menu_items():
    return [
        {"category": group["category"], **item}
        for group in MENU
        for item in group["items"]
    ]


def price_as_number(item):
    return int(item["price"].split()[0])


def summarize_item(item):
    return {
        "name": item["name"],
        "category": item["category"],
        "description": item["description"],
        "price": item["price"],
        "tags": item["tags"],
        "image": item["image"],
        "spice": item["spice"],
        "calories": item["calories"],
        "reason": item.get("reason", "A strong match for your table."),
    }


def recommend_items(preferences):
    mood = preferences.get("mood", "").lower()
    diet = preferences.get("diet", "").lower()
    spice = preferences.get("spice", "").lower()
    budget = preferences.get("budget", "").lower()
    occasion = preferences.get("occasion", "").lower()

    scored = []
    for item in all_menu_items():
        score = 0
        reasons = []

        if mood and mood in item["moods"]:
            score += 4
            reasons.append(f"fits a {mood} mood")
        if occasion and occasion in item["moods"]:
            score += 3
            reasons.append(f"works well for {occasion}")
        if diet and (diet == "any" or diet in item["diet"] or diet in item["tags"]):
            score += 4
            if diet != "any":
                reasons.append(f"matches {diet}")
        if spice == "mild" and item["spice"] <= 1:
            score += 2
            reasons.append("keeps the spice gentle")
        elif spice == "medium" and item["spice"] <= 2:
            score += 2
            reasons.append("has balanced seasoning")
        elif spice == "bold" and item["spice"] >= 2:
            score += 2
            reasons.append("brings a bolder flavor")
        if budget == "value" and price_as_number(item) <= 75:
            score += 2
            reasons.append("keeps the bill lighter")
        elif budget == "premium" and price_as_number(item) >= 120:
            score += 2
            reasons.append("feels more special")

        if "signature" in item["tags"] or "popular" in item["tags"] or "chef pick" in item["tags"]:
            score += 1

        ranked = dict(item)
        ranked["reason"] = ", ".join(reasons[:3]) if reasons else "a balanced guest favorite"
        scored.append((score, ranked))

    scored.sort(key=lambda value: value[0], reverse=True)
    return [summarize_item(item) for _, item in scored[:3]]


def build_ai_reply(message):
    normalized = message.lower()
    items = all_menu_items()

    if any(word in normalized for word in ["hour", "open", "close", "time"]):
        hours = ", ".join(f"{day}: {time}" for day, time in RESTAURANT["hours"].items())
        return f"Our hours are {hours}."
    if any(word in normalized for word in ["reserve", "reservation", "book", "table"]):
        return "You can reserve with the form on this page. Tell me your group size and mood, and I can suggest what to order."
    if any(word in normalized for word in ["vegetarian", "vegan", "meatless"]):
        matches = [item["name"] for item in items if "vegetarian" in item["diet"]]
        return f"Vegetarian picks: {', '.join(matches)}. For something cozy, choose Seven-Vegetable Couscous."
    if any(word in normalized for word in ["seafood", "fish", "calamari"]):
        matches = [item["name"] for item in items if "seafood" in item["diet"]]
        return f"For seafood, I recommend {', '.join(matches)}. Sea Bass is lighter, Calamari is better for sharing."
    if any(word in normalized for word in ["allergy", "allergic", "nuts", "gluten", "dairy"]):
        return "Tell our team about allergies before ordering. I can flag common allergens like gluten, dairy, nuts, fish, and shellfish from the menu."
    if any(word in normalized for word in ["date", "romantic", "special"]):
        return "For a date-night flow: Atlantic Sea Bass, Orange Blossom Panna Cotta, and mint tea. It is bright, elegant, and not too heavy."
    if any(word in normalized for word in ["menu", "dish", "food", "eat", "recommend", "best"]):
        return "My top recommendation is Citrus Chicken Tagine for a classic main. If you want lighter, go Atlantic Sea Bass. If vegetarian, go Seven-Vegetable Couscous."
    if any(word in normalized for word in ["where", "address", "location"]):
        return f"We are at {RESTAURANT['address']}."
    if any(word in normalized for word in ["phone", "call", "contact"]):
        return f"You can reach us at {RESTAURANT['phone']}."

    return "I can recommend dishes by mood, diet, spice level, budget, or occasion. Try asking: What should I order for a cozy vegetarian dinner?"


@app.route("/")
def home():
    return render_template("index.html", restaurant=RESTAURANT, menu=MENU)


@app.post("/api/reservations")
def create_reservation():
    data = request.get_json(silent=True) or {}
    required_fields = ["name", "email", "date", "time", "guests"]
    missing = [field for field in required_fields if not str(data.get(field, "")).strip()]

    if missing:
        return jsonify({"ok": False, "message": "Please complete all reservation fields."}), 400

    try:
        guests = int(data["guests"])
        reservation_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "Please choose a valid date and party size."}), 400

    if guests < 1 or guests > 12:
        return jsonify({"ok": False, "message": "Online reservations support 1 to 12 guests."}), 400

    reservation = {
        "name": data["name"].strip(),
        "email": data["email"].strip(),
        "date": reservation_date.isoformat(),
        "time": data["time"].strip(),
        "guests": guests,
        "notes": data.get("notes", "").strip(),
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
    }
    RESERVATIONS.append(reservation)

    return jsonify(
        {
            "ok": True,
            "message": f"Thanks {reservation['name']}. Your table for {guests} is requested for {reservation['date']} at {reservation['time']}.",
        }
    )


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not message.strip():
        return jsonify({"reply": "Ask me about the menu, opening hours, reservations, or vegetarian dishes."})

    return jsonify({"reply": build_ai_reply(message)})


@app.post("/api/recommendations")
def recommendations():
    preferences = request.get_json(silent=True) or {}
    picks = recommend_items(preferences)
    return jsonify(
        {
            "summary": "Here are the best matches from our menu based on your table preferences.",
            "recommendations": picks,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
