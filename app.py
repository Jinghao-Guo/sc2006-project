from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from Database import database
from Userpreferences import user_preferences
from scoreCalculator import score_calculator
from ai_assistant import get_ai_assistant
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"
app.config["GOOGLE_MAPS_API_KEY"] = os.environ.get("GOOGLE_MAPS_API_KEY", "")


@app.route("/")
def index():
    """Home page with search functionality"""
    preferences = user_preferences.get_preferences()

    # Get favorite flats for display on home page
    favorite_ids = user_preferences.get_favorites()
    favorite_flats = []

    # Get up to 3 favorite flats for preview on home page
    for flat_id in favorite_ids[:3]:
        flat = database.query_id(flat_id)
        if flat:
            flat_dict = dict(flat)
            score = score_calculator.calculate_score(flat_dict, preferences)
            flat_dict["compatibility_score"] = score
            favorite_flats.append(flat_dict)

    return render_template(
        "index.html",
        preferences=preferences,
        has_preferences=user_preferences.has_preferences(),
        favorite_flats=favorite_flats,
        favorites_count=user_preferences.get_favorites_count(),
    )


@app.route("/search")
def search():
    """Search HDB flats based on query parameters with pagination"""
    query = request.args.get("q", "").strip()
    town = request.args.get("town", "").strip()
    flat_type = request.args.get("flat_type", "").strip()
    page = request.args.get("page", 1, type=int)

    # Pagination settings
    per_page = 20  # Show 20 results per page
    offset = (page - 1) * per_page

    # Get total count for pagination
    total_count = database.count_search_results(query, town, flat_type)
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division

    # Get flats for current page
    flats = database.search_flats(query, town, flat_type, limit=per_page, offset=offset)

    # Calculate scores for each flat based on user preferences
    preferences = user_preferences.get_preferences()
    flats_with_scores = []

    for flat in flats:
        # Convert sqlite Row to dict for easier handling
        flat_dict = dict(flat)
        score = score_calculator.calculate_score(flat_dict, preferences)
        flat_dict["compatibility_score"] = score
        flats_with_scores.append(flat_dict)

    # Sort by score if preferences are set, otherwise keep original order (price desc)
    if user_preferences.has_preferences():
        flats_with_scores.sort(key=lambda x: x["compatibility_score"], reverse=True)

    return render_template(
        "search_results.html",
        flats=flats_with_scores,
        query=query,
        town=town,
        flat_type=flat_type,
        has_preferences=user_preferences.has_preferences(),
        page=page,
        total_pages=total_pages,
        total_count=total_count,
        per_page=per_page,
    )


@app.route("/flat/<int:flat_id>")
def flat_detail(flat_id):
    """Show detailed information for a specific HDB flat"""
    flat = database.query_id(flat_id)
    if flat is None:
        return redirect(url_for("index"))

    # Calculate compatibility score and breakdown
    preferences = user_preferences.get_preferences()
    flat_dict = dict(flat)
    score = score_calculator.calculate_score(flat_dict, preferences)
    score_breakdown = score_calculator.get_score_breakdown(flat_dict, preferences)

    return render_template(
        "flat_detail.html",
        flat=flat,
        compatibility_score=score,
        score_breakdown=score_breakdown,
        has_preferences=user_preferences.has_preferences(),
        is_favorite=user_preferences.is_favorite(flat_id),
        google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"],
    )


@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    """Manage user preferences"""
    if request.method == "POST":
        # Set preferences from form data
        flat_type = request.form.get("flat_type", "").strip()
        storey_range = request.form.get("storey_range", "").strip()
        floor_area_sqm = request.form.get("floor_area_sqm", "").strip()
        flat_model = request.form.get("flat_model", "").strip()
        price_range = request.form.get("price_range", "").strip()

        user_preferences.set_preferences(
            flat_type, storey_range, floor_area_sqm, flat_model, price_range
        )
        flash("Your preferences have been saved successfully!", "success")
        return redirect(url_for("index"))

    # GET request - show current preferences
    current_preferences = user_preferences.get_preferences()
    return render_template("preferences.html", preferences=current_preferences)


@app.route("/clear_preferences", methods=["POST"])
def clear_preferences():
    """Clear all user preferences"""
    user_preferences.set_preferences()
    flash("Your preferences have been cleared.", "info")
    return redirect(url_for("index"))


@app.route("/add_to_favorites/<int:flat_id>", methods=["POST"])
def add_to_favorites(flat_id):
    """Add a flat to favorites"""
    # Check if flat exists
    flat = database.query_id(flat_id)
    if flat is None:
        flash("Flat not found.", "error")
        return redirect(url_for("index"))

    if user_preferences.add_to_favorites(flat_id):
        flash("Flat added to your favorites!", "success")
    else:
        flash("This flat is already in your favorites.", "info")

    return redirect(url_for("flat_detail", flat_id=flat_id))


@app.route("/remove_from_favorites/<int:flat_id>", methods=["POST"])
def remove_from_favorites(flat_id):
    """Remove a flat from favorites"""
    if user_preferences.remove_from_favorites(flat_id):
        flash("Flat removed from your favorites.", "info")
    else:
        flash("This flat was not in your favorites.", "warning")

    return redirect(request.referrer or url_for("index"))


@app.route("/favorites")
def favorites():
    """View all favorite flats"""
    favorite_ids = user_preferences.get_favorites()
    favorite_flats = []

    for flat_id in favorite_ids:
        flat = database.query_id(flat_id)
        if flat:
            # Convert to dict and add score
            flat_dict = dict(flat)
            preferences = user_preferences.get_preferences()
            score = score_calculator.calculate_score(flat_dict, preferences)
            flat_dict["compatibility_score"] = score
            favorite_flats.append(flat_dict)

    return render_template(
        "favorites.html",
        flats=favorite_flats,
        has_preferences=user_preferences.has_preferences(),
    )


@app.route("/comparison")
def comparison():
    """Show comparison page for selecting flats"""
    favorite_ids = user_preferences.get_favorites()
    favorite_flats = []

    # Get all favorite flats for selection
    for flat_id in favorite_ids:
        flat = database.query_id(flat_id)
        if flat:
            flat_dict = dict(flat)
            preferences = user_preferences.get_preferences()
            score = score_calculator.calculate_score(flat_dict, preferences)
            flat_dict["compatibility_score"] = score
            favorite_flats.append(flat_dict)

    return render_template(
        "comparison.html",
        flats=favorite_flats,
        has_preferences=user_preferences.has_preferences(),
    )


@app.route("/compare/<int:flat_id1>/<int:flat_id2>")
def compare_flats(flat_id1, flat_id2):
    """Compare two specific flats"""
    # Verify both flats are in favorites
    if not (
        user_preferences.is_favorite(flat_id1)
        and user_preferences.is_favorite(flat_id2)
    ):
        flash("Both flats must be in your favorites to compare them.", "error")
        return redirect(url_for("favorites"))

    # Get both flats
    flat1 = database.query_id(flat_id1)
    flat2 = database.query_id(flat_id2)

    if not flat1 or not flat2:
        flash("One or both flats could not be found.", "error")
        return redirect(url_for("favorites"))

    # Calculate scores and breakdowns for both flats
    preferences = user_preferences.get_preferences()

    flat1_dict = dict(flat1)
    flat1_score = score_calculator.calculate_score(flat1_dict, preferences)
    flat1_breakdown = score_calculator.get_score_breakdown(flat1_dict, preferences)

    flat2_dict = dict(flat2)
    flat2_score = score_calculator.calculate_score(flat2_dict, preferences)
    flat2_breakdown = score_calculator.get_score_breakdown(flat2_dict, preferences)

    return render_template(
        "compare_result.html",
        flat1=flat1,
        flat2=flat2,
        flat1_score=flat1_score,
        flat2_score=flat2_score,
        flat1_breakdown=flat1_breakdown,
        flat2_breakdown=flat2_breakdown,
        has_preferences=user_preferences.has_preferences(),
    )


@app.route("/ai_chat", methods=["GET", "POST"])
def ai_chat():
    """AI Assistant chat interface"""
    return render_template(
        "ai_chat.html", has_preferences=user_preferences.has_preferences()
    )


@app.route("/api/ai/chat", methods=["POST"])
def api_ai_chat():
    """API endpoint for AI chat"""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        conversation_history = data.get("history", [])

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Get AI assistant and generate response
        assistant = get_ai_assistant()
        response = assistant.chat(user_message, conversation_history)

        return jsonify({"response": response, "success": True})

    except ValueError as e:
        return jsonify({"error": str(e), "success": False}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}", "success": False}), 500


@app.route("/api/ai/analyze_flat/<int:flat_id>", methods=["GET"])
def api_analyze_flat(flat_id):
    """API endpoint for AI flat analysis"""
    try:
        assistant = get_ai_assistant()
        analysis = assistant.ask_about_flat(flat_id)
        return jsonify({"analysis": analysis, "success": True})
    except ValueError as e:
        return jsonify({"error": str(e), "success": False}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}", "success": False}), 500


@app.route("/api/ai/compare/<int:flat_id1>/<int:flat_id2>", methods=["GET"])
def api_compare_flats(flat_id1, flat_id2):
    """API endpoint for AI flat comparison"""
    try:
        assistant = get_ai_assistant()
        comparison = assistant.compare_flats(flat_id1, flat_id2)
        return jsonify({"comparison": comparison, "success": True})
    except ValueError as e:
        return jsonify({"error": str(e), "success": False}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}", "success": False}), 500


if __name__ == "__main__":
    app.run(debug=True)
