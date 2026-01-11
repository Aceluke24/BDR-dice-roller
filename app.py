from flask import Flask, render_template, request, session
import random

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
                # Multi-dice: original match logic
                non_six = [r for r in rolls if r != 6]
                session["base"] = non_six[0] if non_six else None
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

    dice_images = [f"dice{r}.png" for r in session["rolls"]]

    return render_template(
        "index.html",
        dice_images=dice_images,
        can_bonus=session["can_bonus"],
        num_dice=session["num_dice"]
    )


if __name__ == "__main__":
    app.run(debug=True)
