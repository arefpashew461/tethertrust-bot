import logging


# -------------------------
# TetherTrust Logger System
# -------------------------


logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )

)



logger = logging.getLogger(
    "TetherTrust"
)