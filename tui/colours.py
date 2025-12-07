# Define colours

def rgb(r: int, g: int, b: int, bg: bool = False) -> str:
    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"

def col(code: int, bg: bool = False): # 256 colours
    return f"\033[{48 if bg else 38};5;{code}m"

RESET = '\033[0m'
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# --- Base Palette ---
WHITE = col(231)            # Pure white, for highlights
BASE_COL = col(254)         # Main text colour, a very light grey
LIGHT_GREY = col(248)       # Lighter grey for secondary text
DARK_GREY = col(240)        # Darker grey for subtle text/borders

# --- Theme Colours ---
TITLE_COL = col(215)        # Primary theme colour (light orange)
ACCENT_COL = col(222)       # Accent/selection colour (light yellow-orange)

# --- State Colours ---
SUCCESS_COL = col(77)       # A clear, pleasant green
ERROR_COL = col(197)        # A clear, unambiguous red
LIGHT_YELLOW = col(221)     # A mellow yellow for warnings or highlights

# --- UI Element Colours ---
# Cards
CARD_IDX_COL = LIGHT_GREY
CARD_TERM_COL = BASE_COL
CARD_DEF_COL = LIGHT_GREY

# Decks
DECK_IDX_COL = LIGHT_GREY
DECK_NAME_COL = BASE_COL

def _main():
    for i in range(256):  # Palette viewer
        print(f"{col(i, True)}{col(0)} {i:3} {RESET}", end="")
        if (i + 1) % 16 == 0:
            print()

if __name__ == "__main__":
    _main()