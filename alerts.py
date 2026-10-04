# -------------------------
# TetherTrust Alert System
# -------------------------

def calculate_change(
    current,
    previous
):
    """
    محاسبه درصد و مقدار تغییر
    """

    if not previous:

        return 0, 0


    amount = current - previous


    percent = (
        amount
        /
        previous
        *
        100
    )


    return amount, percent



def create_alert(
    current,
    previous
):
    """
    ساخت هشدار هوشمند بازار

    سطح 1:
    تغییر 0.5 درصد

    سطح 2:
    تغییر 1 درصد
    """


    amount, percent = calculate_change(
        current,
        previous
    )


    if abs(percent) < 0.5:

        return None



    if percent >= 1:

        level = "🚨 هشدار مهم"


    elif percent <= -1:

        level = "🚨 هشدار مهم"


    else:

        level = "⚠️ هشدار بازار"



    if percent > 0:

        direction = (
            f"▲ +{percent:.2f}%"
        )

    else:

        direction = (
            f"▼ {percent:.2f}%"
        )



    text = f"""
{level}

💠 TETHERTRUST

📊 تغییر قیمت:
{direction}

💵 قیمت فعلی:
{current:,} تومان

💰 تغییر مبلغ:
{amount:+,} تومان

━━━━━━━━━━

مرجع تخصصی قیمت تتر
"""


    return text