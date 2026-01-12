from flask import Flask, render_template, request, session
import random
from collections import Counter

app = Flask(__name__)
app.secret_key = "dice_secret"


def get_base(rolls):
    """Return the first non-6 number as base, or None if all 6s."""
    for r in rolls:
        if r != 6:
            return r
    return None


def can_continue_bonus(roll, base):
    """Return True if bonus can continue (roll matches base or is 6)."""
    if base is None:
        return roll == 6  # still all 6s
    return roll == base or roll == 6


def calculate_scores(rolls):
    """Calculate match scores for each die value."""
    counts = Counter(rolls)
    # Sort by count (descending), then by die value (descending)
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], -x[0]))
    return sorted_counts


@app.route("/", methods=["GET", "POST"])
def index():
    # --- SAFE SESSION INITIALIZATION ---
    session.setdefault("rolls", [])
    session.setdefault("base", None)
    session.setdefault("can_bonus", False)
    session.setdefault("num_dice", "")

    if request.method == "POST":
        action = request.form["action"]
        num_dice = int(request.form.get("num_dice", session.get("num_dice", 1)))
        session["num_dice"] = num_dice

        # --- INITIAL ROLL ---
        if action == "roll":
            rolls = [random.randint(1, 6) for _ in range(num_dice)]
            session["rolls"] = rolls

            if num_dice == 1:
                # Single die: bonus only if first roll is 6
                if rolls[0] == 6:
                    session["base"] = None  # base not known yet
                    session["can_bonus"] = True
                else:
                    session["base"] = rolls[0]
                    session["can_bonus"] = False
            else:
                # Multi-dice: base is the most common non-6 number
                non_six = [r for r in rolls if r != 6]
                if non_six:
                    # Find the most common non-6 number
                    counts = Counter(non_six)
                    session["base"] = counts.most_common(1)[0][0]
                else:
                    session["base"] = None
                session["can_bonus"] = len(set(non_six)) <= 1

        # --- BONUS ROLL ---
        elif action == "bonus" and session.get("can_bonus", False):
            bonus = random.randint(1, 6)
            session["rolls"].append(bonus)

            # Determine base if it wasn't set yet
            if session["num_dice"] == 1 and session["base"] is None and bonus != 6:
                session["base"] = bonus

            # Can continue bonus?
            if session["num_dice"] == 1:
                session["can_bonus"] = can_continue_bonus(bonus, session["base"])
            else:
                # Multi-dice: bonus continues if matches base or 6
                session["can_bonus"] = can_continue_bonus(bonus, session["base"])

    # Group dice by value for display
    grouped_dice = {}
    for roll in session["rolls"]:
        if roll not in grouped_dice:
            grouped_dice[roll] = []
        grouped_dice[roll].append(f"dice{roll}.png")
    
    # Sort groups: by count (descending), then by value (descending)
    sorted_groups = sorted(grouped_dice.items(), 
                          key=lambda x: (-len(x[1]), -x[0]))
    
    # Calculate matching dice count (base number + sixes)
    match_count = 0
    if session["rolls"]:
        if session["base"] is not None:
            match_count = sum(1 for r in session["rolls"] if r == session["base"] or r == 6)
        else:
            # All sixes case
            match_count = sum(1 for r in session["rolls"] if r == 6)

    return render_template(
        "index.html",
        grouped_dice=sorted_groups,
        can_bonus=session["can_bonus"],
        num_dice=session["num_dice"],
        base_number=session["base"],
        match_count=match_count
    )


# if __name__ == "__main__":
#     app.run(debug=False, host='0.0.0.0')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)