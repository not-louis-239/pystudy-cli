# Define colours

def rgb(r: int, g: int, b: int, bg: bool = False) -> str:
    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"

def col(code: int, bg: bool = False): # 256 colours
    return f"\033[{48 if bg else 38};5;{code}m"

WHITE = col(231)
LGREY = col(146)
DGREY = col(103)

RESET = '\033[0m'
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

if __name__ == "__main__":
    for i in range(256):  # Palette viewer
        print(f"{col(i, True)}{col(0)} {i:3} {RESET}", end="")
        if (i + 1) % 16 == 0:
            print()