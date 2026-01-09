from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = "dice_secret"


def is_match(rolls):
    non_six = [r for r in rolls if r != 6]
    return len(set(non_six)) <= 1


@app.route("/", methods=["GET", "POST"])
def index():
    # --- SAFE SESSION INITIALIZATION ---
    session.setdefault("rolls", [])
    session.setdefault("base", None)
    session.setdefault("can_bonus", False)
    session.setdefault("num_dice", "")

    if request.method == "POST":
        action = request.form["action"]

        # INITIAL ROLL
        if action == "roll":
            num_dice = int(request.form["num_dice"])
            session["num_dice"] = num_dice

            rolls = [random.randint(1, 6) for _ in range(num_dice)]
            session["rolls"] = rolls

            if is_match(rolls):
                non_six = [r for r in rolls if r != 6]
                session["base"] = non_six[0] if non_six else None
                session["can_bonus"] = True
            else:
                session["base"] = None
                session["can_bonus"] = False

        # BONUS ROLL
        elif action == "bonus":
            bonus = random.randint(1, 6)
            session["rolls"].append(bonus)

            # All-6s case: first non-6 sets base
            if session["base"] is None and bonus != 6:
                session["base"] = bonus
                session["can_bonus"] = True

            # Continue match
            elif bonus == session["base"] or bonus == 6:
                session["can_bonus"] = True

            else:
                session["can_bonus"] = False

    dice_images = [f"dice{r}.png" for r in session["rolls"]]

    return render_template(
        "index.html",
        dice_images=dice_images,
        can_bonus=session["can_bonus"],
        num_dice=session["num_dice"]
    )


if __name__ == "__main__":
    app.run(debug=True)
