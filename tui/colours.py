# Define colours

def rgb(r: int, g: int, b: int, bg: bool = False) -> str:
    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"

def col(code: int, bg: bool = False): # 256 colours
    return f"\033[{48 if bg else 38};5;{code}m"

WHITE = col(231)
LGREY = col(146)
DGREY = col(103)
BASE_COL = DGREY

RESET = '\033[0m'
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Custom colours
TITLE_COL = col(222)
SUCCESS_COL = col(120)
ERROR_COL = col(210)
AQUAMARINE = col(48)
LIGHT_YELLOW = col(229)
LIGHT_BLUE = col(45)

CARD_IDX_COL = col(195)
CARD_TERM_COL = LGREY
CARD_DEF_COL = BASE_COL

DECK_IDX_COL = col(121)
DECK_NAME_COL = col(189)

def _main():
    for i in range(256):  # Palette viewer
        print(f"{col(i, True)}{col(0)} {i:3} {RESET}", end="")
        if (i + 1) % 16 == 0:
            print()

if __name__ == "__main__":
    _main()