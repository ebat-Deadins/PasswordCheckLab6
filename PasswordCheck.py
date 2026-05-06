import string, os, sys, math
from pathlib import Path

if os.name == 'nt':
    import ctypes
    ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
    import msvcrt
else:
    import tty, termios

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

FILE_PATH = Path(__file__).parent / "blacklist.txt"
MAX_SCORE = 7

# ── Шалгуурууд ────────────────────────────────────────────────────────────────

def check_length(pw):
    n = len(pw)
    if n < 8:  return 0, "Дор хаяж 8 тэмдэгт байх ёстой"
    if n < 12: return 1, "Урт боломжийн (12+ илүү найдвартай)"
    return 2,          "Урт хангалттай"

def check_upper_lower(pw):
    if any(c.isupper() for c in pw) and any(c.islower() for c in pw):
        return 1, "Том ба жижиг үсэг хоёулаа байна"
    return 0, "Том (A-Z) ба жижиг (a-z) үсэг хоёулаа шаардлагатай"

def check_digits(pw):
    if any(c.isdigit() for c in pw):
        return 1, "Тоо агуулсан"
    return 0, "Дор хаяж нэг тоо (0-9) оруулна уу"

def check_symbols(pw):
    if any(c in string.punctuation for c in pw):
        return 1, "Тусгай тэмдэгт агуулсан (!@#$...)"
    return 0, "Тусгай тэмдэгт (!@#$%^&*...) байх ёстой"

def check_dictionary(pw):
    try:
        blacklist = {l.strip().lower() for l in FILE_PATH.open(encoding='utf-8') if l.strip()}
        for word in blacklist:
            if word in pw.lower():
                return 0, f"'{word}' - амархан таагдах үг орсон байна"
        return 1, "Түгээмэл сул үг агуулаагүй"
    except FileNotFoundError:
        return 1, "Blacklist шалгалт алгасав (файл олдсонгүй)"

def check_no_repeats(pw):
    # "aaaa" "1111" гэх мэт давтагдсан тэмдэгт шалгах
    if len(pw) >= 3 and any(pw[i] == pw[i+1] == pw[i+2] for i in range(len(pw)-2)):
        return 0, "Ижил тэмдэгт дараалан давтагдсан (aaa, 111...)"
    return 1, "Давтагдсан тэмдэгт байхгүй"

def calc_score(pw):
    total, msgs = 0, []
    for fn in (check_length, check_upper_lower, check_digits, check_symbols, check_dictionary, check_no_repeats):
        s, m = fn(pw)
        total += s
        msgs.append((s, m))
    return total, msgs

# ── Энтропи (мэдээллийн нягт) ────────────────────────────────────────────────

def entropy(pw):
    if not pw: return 0
    pool = 0
    if any(c.islower() for c in pw):             pool += 26
    if any(c.isupper() for c in pw):             pool += 26
    if any(c.isdigit() for c in pw):             pool += 10
    if any(c in string.punctuation for c in pw): pool += 32
    return round(len(pw) * math.log2(pool)) if pool else 0

def entropy_label(bits):
    if bits < 28:  return f"{RED}{bits} bit - маш сул{RESET}"
    if bits < 36:  return f"{YELLOW}{bits} bit - дунд{RESET}"
    if bits < 60:  return f"{GREEN}{bits} bit - сайн{RESET}"
    return             f"{GREEN}{BOLD}{bits} bit - маш найдвартай{RESET}"

# ── Дараагийн алхам санал болгох (hint) ──────────────────────────────────────

def next_hint(msgs):
    for s, m in msgs:
        if s == 0:
            return f"{CYAN}Зөвлөгөө: {m}{RESET}"
    return f"{GREEN}Бүх шаардлага хангасан!{RESET}"

# ── Хүч мөр (strength bar) ────────────────────────────────────────────────────

LABELS = ["Маш сул","Маш сул","Сул","Дунд","Сайн","Маш сайн","Маш сайн","Маш сайн"]

def strength_bar(score):
    filled = round(score / MAX_SCORE * 22)
    bar    = "#" * filled + "." * (22 - filled)
    color  = RED if score <= 2 else YELLOW if score <= 4 else GREEN
    label  = LABELS[min(score, 7)]
    return f"{color}[{bar}] {label}{RESET}"

# ── Товчлуур унших ────────────────────────────────────────────────────────────

def get_key():
    if os.name == 'nt':
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'): msvcrt.getch(); return None
        return ch
    fd, old = sys.stdin.fileno(), termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setraw(fd)
        return sys.stdin.buffer.read(1)   # байт зөв уншина (multi-byte fix)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ── Үндсэн гогцоо ─────────────────────────────────────────────────────────────

def main():
    pw, show = "", False

    while True:
        sys.stdout.write("\033[H\033[2J\033[3J"); sys.stdout.flush()

        score, msgs = calc_score(pw)
        bits        = entropy(pw)
        masked      = pw if show else "*" * len(pw)
        toggle      = "nuuh" if show else "haruulah"

        print(f"{BOLD}=== Nuuts ugiin huch shalgagch ==={RESET}\n")
        print(f"  Nuuts ug : {masked}_")
        print(f"  Huch     : {strength_bar(score)}")
        print(f"  Entropi  : {entropy_label(bits)}")
        print(f"  Onoo     : {score}/{MAX_SCORE}\n")
        print("  " + "-" * 44)

        for s, m in msgs:
            icon = f"{GREEN}+{RESET}" if s > 0 else f"{RED}-{RESET}"
            print(f"  [{icon}] {m}")

        print("  " + "-" * 44)
        print(f"  {next_hint(msgs)}\n")
        print(f"  {GRAY}[Enter] Batalgaajuulah  [Tab] {toggle}  [Ctrl+C] Garах{RESET}")

        ch = get_key()
        if ch is None:               continue
        if ch in (b'\r', b'\n'):     break
        if ch == b'\t':              show = not show
        if ch == b'\x03':            print(); sys.exit(0)
        if ch in (b'\x08', b'\x7f'): pw = pw[:-1]
        else:
            try:
                c = ch.decode('utf-8')
                if c.isprintable(): pw += c
            except UnicodeDecodeError:
                pass

    print(f"\n  {GREEN}Nuuts ug batalgaajlaa!{RESET}\n")

if __name__ == "__main__":
    main()
