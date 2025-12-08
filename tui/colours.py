# Define colours

def rgb(r: int, g: int, b: int, bg: bool = False) -> str:
    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"

def col(code: int, bg: bool = False): # 256 colours
    return f"\033[{48 if bg else 38};5;{code}m"

RESET = '\033[0m'
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Base palette
WHITE = col(231)            # Pure white, for highlights
BASE_COL = col(254)         # Main text colour, a very light grey
LIGHT_GREY = col(248)       # Lighter grey for secondary text
DARK_GREY = col(240)        # Darker grey for subtle text/borders

# Theme colours
TITLE_COL = col(215)        # Primary theme colour (light orange)
ACCENT_COL = col(222)       # Accent/selection colour (light yellow-orange)

# State colours
SUCCESS_COL = col(77)       # A clear, pleasant green
ERROR_COL = col(197)        # A clear, unambiguous red
LIGHT_YELLOW = col(221)     # A mellow yellow for warnings or highlights

# Cards
CARD_IDX_COL = LIGHT_GREY
CARD_TERM_COL = BASE_COL
CARD_DEF_COL = LIGHT_GREY

# Decks
DECK_IDX_COL = LIGHT_GREY
DECK_NAME_COL = BASE_COL
LEARNING_COL = LIGHT_YELLOW

# Minimap colours
UNANSWERED1_COL = col(239)
UNANSWERED2_COL = col(242)
ANSWERED1_COL = col(247)
ANSWERED2_COL = col(250)
CURRENT_COL = ACCENT_COL

def _main():
    print("=== 256-Color Palette ===")
    for i in range(256):  # Palette viewer
        print(f"{col(i, False)} {i:3} {RESET}", end="")
        if (i + 1) % 16 == 0:
            print()

    print("\n=== Application Colour Palette ===")
    print(f"{WHITE}WHITE: Sample Text{RESET}")
    print(f"{BASE_COL}BASE_COL: Sample Text{RESET}")
    print(f"{LIGHT_GREY}LIGHT_GREY: Sample Text{RESET}")
    print(f"{DARK_GREY}DARK_GREY: Sample Text{RESET}")
    print(f"{TITLE_COL}TITLE_COL: Sample Text{RESET}")
    print(f"{ACCENT_COL}ACCENT_COL: Sample Text{RESET}")
    print(f"{SUCCESS_COL}SUCCESS_COL: Sample Text{RESET}")
    print(f"{ERROR_COL}ERROR_COL: Sample Text{RESET}")
    print(f"{LIGHT_YELLOW}LIGHT_YELLOW: Sample Text{RESET}")
    print(f"{CARD_IDX_COL}CARD_IDX_COL: Sample Text{RESET}")
    print(f"{CARD_TERM_COL}CARD_TERM_COL: Sample Text{RESET}")
    print(f"{CARD_DEF_COL}CARD_DEF_COL: Sample Text{RESET}")
    print(f"{DECK_IDX_COL}DECK_IDX_COL: Sample Text{RESET}")
    print(f"{DECK_NAME_COL}DECK_NAME_COL: Sample Text{RESET}")
    print(f"{LEARNING_COL}LEARNING_COL: Sample Text{RESET}")

if __name__ == "__main__":
    _main()