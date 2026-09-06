# -*- coding: utf-8 -*-
"""
RAIN Console Art Engine
==========================
- Windows / Linux 터미널 색상 자동 활성화 (ANSI / VT)
- 메인 화면 아트 배너 + 진입 시 화면 전체에 글자가 좌르륵 쏟아지는 레인 연출
- 공격 실행 시 '문단별 조르륵' 연출 (타자기 + 단락 폭포 출력)
- 공격 진행 중 1초 단위 실시간 상태바
- 대화형 메인 메뉴 (공격 마법사 / 툴 콘솔 / 명령어 직접 실행)

이 모듈은 start.py 에서 import 되어 사용됩니다.
단독 실행(python ddos_art.py) 시 연출 미리보기 데모로 동작합니다.
"""
import os
import sys
import time
import shutil
import ctypes
import subprocess


# ---------------------------------------------------------------------------
# ANSI 색상 상수
# ---------------------------------------------------------------------------
class C:
    R = "\x1b[91m"     # 밝은 빨강
    G = "\x1b[92m"     # 밝은 초록
    Y = "\x1b[93m"     # 밝은 노랑
    B = "\x1b[94m"     # 밝은 파랑
    M = "\x1b[95m"     # 밝은 자홍
    CY = "\x1b[96m"    # 밝은 청록
    W = "\x1b[97m"     # 밝은 흰색
    DIM = "\x1b[2m"
    BOLD = "\x1b[1m"
    UND = "\x1b[4m"
    REV = "\x1b[7m"
    RST = "\x1b[0m"


# 배너에 사용할 무지개 계열 색 순환
RAINBOW = [C.M, C.CY, C.W, C.CY, C.G, C.Y, C.R, C.M]


# ---------------------------------------------------------------------------
# 그림(아트) 원문  -- pyfiglet(font: slant) 으로 생성
# ---------------------------------------------------------------------------
MAIN_ART = """    ____  ___    _____   __
   / __ \\/   |  /  _/ | / /
  / /_/ / /| |  / //  |/ /
 / _, _/ ___ |_/ // /|  /
/_/ |_/_/  |_/___/_/ |_/
"""

ATTACK_ART = """    ___  _______________   ________ __
   /   |/_  __/_  __/   | / ____/ //_/
  / /| | / /   / / / /| |/ /   / ,<
 / ___ |/ /   / / / ___ / /___/ /| |
/_/  |_/_/   /_/ /_/  |_\\____/_/ |_|
"""

FINISH_ART = """    ___________   ___________ __  __
   / ____/  _/ | / /  _/ ___// / / /
  / /_   / //  |/ // / \\__ \\/ /_/ /
 / __/ _/ // /|  // / ___/ / __  /
/_/   /___/_/ |_/___//____/_/ /_/
"""

# 서브 화면(메뉴 1~5 선택 시) 전용 배너
LAYER7_ART = """    __    _____  ____________     _____
   / /   /   \\ \\/ / ____/ __ \\   /__  /
  / /   / /| |\\  / __/ / /_/ /_____/ /
 / /___/ ___ |/ / /___/ _, _/_____/ /
/_____/_/  |_/_/_____/_/ |_|     /_/
"""

LAYER4_ART = """    __    _____  ____________        __ __
   / /   /   \\ \\/ / ____/ __ \\      / // /
  / /   / /| |\\  / __/ / /_/ /_____/ // /_
 / /___/ ___ |/ / /___/ _, _/_____/__  __/
/_____/_/  |_/_/_____/_/ |_|        /_/
"""

TOOLS_ART = """  __________  ____  __   _____
 /_  __/ __ \\/ __ \\/ /  / ___/
  / / / / / / / / / /   \\__ \\
 / / / /_/ / /_/ / /______/ /
/_/  \\____/\\____/_____/____/
"""

METHODS_ART = """    __  _________________  ______  ____  _____
   /  |/  / ____/_  __/ / / / __ \\/ __ \\/ ___/
  / /|_/ / __/   / / / /_/ / / / / / / /\\__ \\
 / /  / / /___  / / / __  / /_/ / /_/ /___/ /
/_/  /_/_____/ /_/ /_/ /_/\\____/_____//____/
"""

EXPERT_ART = """    _______  __ ____  __________  ______
   / ____/ |/ // __ \\/ ____/ __ \\/_  __/
  / __/  |   // /_/ / __/ / /_/ / / /
 / /___ /   |/ ____/ /___/ _, _/ / /
/_____//_/|_/_/   /_____/_/ |_| /_/
"""


# ---------------------------------------------------------------------------
# Brain 스타일 로고 & 패널  -- 참조 화면 (brain1 /brain2) 재현
# ---------------------------------------------------------------------------
BRAIN_ART = r""" ____  _____            _____ _   _ 
|  _ \|  __ \     /\   |_   _| \ | |
| |_) | |__) |   /  \    | | |  \| |
|  _ <|  _  /   / /\ \   | | | . ` |
| |_) | | \ \  / ____ \ _| |_| |\  |
|____/|_|  \_\/_/    \_\_____|_| \_|
"""

BRAIN_HEADER_USER = "shavsheti"
BRAIN_HEADER = ("shavsheti  [ ]  DISCORD:  braindevs.  [ ]  Power Upgraded .  New Design!")
BRAIN_TAGLINE = "Progress, not perfection."
BRAIN_WELCOME_1 = "Welcome To The Start Screen Of BrainNetv5.0"
BRAIN_WELCOME_2 = "Powered By Brainv9 , Ran by Gecko"
BRAIN_DISCORD = "-  https://discord.gg/HsMBBPZAW  -"
BRAIN_HELP = 'Type "help" For the list of commands'
BRAIN_COPY = "Copyright © 2026 Brain all rights reserved"
BRAIN_PROMPT_USER = "shavsheti"
BRAIN_PROMPT_NAME = "Brain"


_VERSION = "v2.4 SNAPSHOT"
_METHOD_COUNT = "56+"

# ---------------------------------------------------------------------------
# 메인 화면 '글자 좌르륵(레인)' 설정
# ---------------------------------------------------------------------------
RAIN_FIRST_SEC = 2.6     # 프로그램 시작 직후 첫 메인 화면의 폭포 지속 시간
RAIN_REPEAT_SEC = 1.1    # 공격/작업 후 메인으로 복귀할 때의 폭포 지속 시간
RAIN_CHARS = "01ABCDEF#$%&@*+=^~[]{}|;:.,-_<>/\\"
_RAIN_PLAYED = False     # 최초 진입 여부 (메인 화면 효과용)

# ---------------------------------------------------------------------------
# 콘솔 초기화
# ---------------------------------------------------------------------------
_COLOR = True          # 색상 사용 여부
_INIT_DONE = False     # 초기화 1회 여부


def init():
    """Windows 콘솔에서 VT(ANSI) 처리를 켜고 색상 지원 여부를 판단한다."""
    global _COLOR, _INIT_DONE
    if _INIT_DONE:
        return _COLOR
    _INIT_DONE = True

    if os.environ.get("NO_COLOR"):
        _COLOR = False
        return _COLOR

    if os.name == "nt":                      # Windows: cmd / powershell
        try:
            k32 = ctypes.windll.kernel32
            out = k32.GetStdHandle(-11)      # STD_OUTPUT_HANDLE
            mode = ctypes.c_uint32()
            if k32.GetConsoleMode(out, ctypes.byref(mode)):
                VT = 0x0004                  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                k32.SetConsoleMode(out, mode.value | VT)
        except Exception:
            pass

    _COLOR = bool(sys.stdout and sys.stdout.isatty())
    return _COLOR


def is_color():
    return _COLOR


def paint(text, code, bold=False):
    """색상 코드로 감싼 문자열 반환. 색상 미지원 시 원문 그대로."""
    if not _COLOR:
        return text
    return f"{C.BOLD if bold else ''}{code}{text}{C.RST}"


def clear_screen():
    if _COLOR:
        print("\x1b[2J\x1b[H", end="", flush=True)
    else:
        print("\n" * 3)


# ---------------------------------------------------------------------------
# 출력 효과
# ---------------------------------------------------------------------------
def typewrite(text, delay=0.004, end="\n"):
    """한 글자씩 흘러내리듯 출력 (조르륵)."""
    for ch in text:
        print(ch, end="", flush=True)
        if delay:
            time.sleep(delay)
    print(end=end, flush=True)


def cascade(lines, delay=0.002, color=None, indent="", pause=0.0):
    """여러 줄을 위에서 아래로 빠르게 흘려보낸다."""
    for ln in lines:
        if color:
            ln = paint(ln, color)
        typewrite(indent + ln, delay=delay)
        if pause:
            time.sleep(pause)


def pour(paragraphs, para_gap=0.16, char_delay=0.003, indent="  "):
    """
    '문단별 조르륵' 폭포 출력.

    paragraphs : list of list[str]  (문단 -> 줄들)
    각 문단이 끝나면 잠깐 멈췄다가 다음 문단이 주르륵 흘러내린다.
    """
    first = True
    for para in paragraphs:
        if not first:
            time.sleep(para_gap)
        first = False
        if isinstance(para, str):
            para = [para]
        for ln in para:
            typewrite(indent + ln, delay=char_delay)
        print("", flush=True)


def banner_rainbow(art, color_cycle=None):
    """아트 각 줄에 무지개 색을 순환 입힌다."""
    cycle = color_cycle or RAINBOW
    lines = art.rstrip("\n").split("\n")
    out = []
    for i, ln in enumerate(lines):
        if ln.strip():
            out.append(paint(ln, cycle[i % len(cycle)], bold=True))
        else:
            out.append("")
    return out


def term_width():
    try:
        return shutil.get_terminal_size((100, 24)).columns
    except Exception:
        return 100


def _term_wh():
    """현재 터미널 크기 (가로, 세로). 측정 불가 시 안전 기본값."""
    try:
        sz = shutil.get_terminal_size((100, 25))
        w = max(30, min(sz.columns, 220))
        h = max(10, min(sz.lines, 60))
        return w, h
    except Exception:
        return 100, 25


# ---------------------------------------------------------------------------
# 디지털 문자 폭포 (레인) -- '글자가 좌르륵' 연출
# ---------------------------------------------------------------------------
def matrix_rain(seconds=2.0, fps=32, cols=0, rows=0,
                head_prob=0.005, near_prob=0.03, dim_prob=0.16,
                head_code="\x1b[97;1m", near_code="\x1b[92m",
                dim_code="\x1b[32m"):
    """
    터미널 전체에 글자가 좌르륵 쏟아지는 디지털 폭포(레인) 연출.

    각 세로 줄(컬럼)이 제각각의 속도로 아래로 흘러내리며,
    머리 글자는 밝게, 뒤따르는 글자는 점점 어둡게 번진다.
    색상이 꺼져 있거나 실제 터미널(콘솔)이 아니면 아무것도 하지 않는다.
    """
    if not (_COLOR and sys.stdout and sys.stdout.isatty()):
        return
    if seconds <= 0:
        return

    import random as _rnd

    if cols > 0 and rows > 0:
        W, H = cols, rows
    else:
        W, H = _term_wh()
        H = max(6, H - 1)          # 맨 아래 한 줄은 예약

    hp, np_, dp = head_prob, near_prob, dim_prob
    n_chars = len(RAIN_CHARS)
    rnd = _rnd.random

    # 컬럼별 '흘러내린 위치'와 속도 (속도는 수시로 변해 자연스러운 흐름을 만든다)
    off = [rnd() * 5000.0 for _ in range(W)]
    spd = [_rnd.uniform(0.5, 1.35) for _ in range(W)]

    rst = C.RST
    hide = "\x1b[?25l"
    show = "\x1b[?25h"
    step = 1.0 / max(1, fps)
    next_tick = time.time()
    deadline = next_tick + seconds

    sys.stdout.write(hide)
    try:
        while True:
            now = time.time()
            if now >= deadline:
                break

            for c in range(W):
                off[c] += spd[c]
                if rnd() < 0.03:
                    spd[c] = _rnd.uniform(0.5, 1.35)

            frame = ["\x1b[H"]
            for r in range(H):
                row = []
                for c in range(W):
                    k = int(off[c]) - r        # 문자 테이프 상 위치 (아래로 흐름)
                    # 컬럼/위치 기반 결정적 난수 -> 깜빡임 없이 안정적인 이끼(꼬리)
                    v = c * 2246822519 + k * 3266489917
                    v ^= v >> 15
                    v &= 0x7fffffff
                    frac = (v % 100000) * 1e-5
                    if frac < hp:
                        ch = RAIN_CHARS[(k + c * 5) % n_chars]
                        row.append(head_code + ch + rst)
                    elif frac < hp + np_:
                        ch = RAIN_CHARS[(k * 3 + c * 7) % n_chars]
                        row.append(near_code + ch + rst)
                    elif frac < hp + np_ + dp:
                        ch = RAIN_CHARS[(k * 7 + c * 11) % n_chars]
                        row.append(dim_code + ch + rst)
                    else:
                        row.append(" ")
                frame.append("".join(row))
            # 커서를 맨 위로 올려 한 화면을 통째로 덮어쓴다
            sys.stdout.write("\n".join(frame) + "\x1b[0J")
            sys.stdout.flush()

            next_tick += step
            delay = next_tick - time.time()
            if delay > 0:
                time.sleep(delay)
    except KeyboardInterrupt:
        pass                     # Ctrl+C 로 인트로 건너뛰기 허용
    finally:
        sys.stdout.write("\x1b[2J\x1b[H" + show)
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# 메인 화면
# ---------------------------------------------------------------------------
_BOOT_LINES = [
    ("ESTABLISHING C2 UPLINK", "ONLINE"),
    ("DECRYPTING PACKET PAYLOAD GRID", "UNLOCKED"),
    ("MOUNTING LAYER-7 / LAYER-4 LAUNCHERS", "56+ UNITS"),
    ("HANDSHAKE WITH ANONYMOUS GATEWAYS", "STANDBY"),
]


_BOOT_SHOWN = False     # 부팅 로그(스트림)는 최초 1회만 출력


# ---------------------------------------------------------------------------
# Brain 스타일 렌더링 헬퍼 (뉴1 / 뉴2 스타일)
# ---------------------------------------------------------------------------
_BOX_V = "|"
_BOX_H = "-"
_BOX_TL = "/"
_BOX_TR = "\\"
_BOX_BL = "\\"
_BOX_BR = "/"

# ANSI 256색 팔레트에서 빨강 계열 (어두움 -> 밝음 그라데이션 룩)
def _red_grad(i, n):
    """i(0..n-1) 에 따라 어두운 빨강 -> 밝은 빨강 256색 코드 반환."""
    if n <= 1:
        return "\x1b[38;5;160m"
    steps = [88, 124, 160, 196, 202, 208, 214, 220]   # 어두움 -> 밝음 (빨강->주황)
    t = i / (n - 1)
    idx = t * (len(steps) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(steps) - 1)
    frac = idx - lo
    base = steps[lo]
    nxt = steps[hi]
    # 256색 코드 사이 보간이 불가하므로 가까운 쪽으로 스냅
    pick = steps[lo] if frac < 0.5 else steps[hi]
    return f"\x1b[38;5;{pick}m"


def brain_logo(art=BRAIN_ART):
    """'BRAIN' 로고를 왼쪽(어두움)->오른쪽(밝음) 빨강 그라데이션으로 찍는다."""
    lines = art.rstrip("\n").split("\n")
    W = max((len(l) for l in lines), default=0)
    out = []
    for ln in lines:
        row = []
        for c, ch in enumerate(ln):
            if ch == " ":
                row.append(" ")
            else:
                code = _red_grad(c, W)
                if _COLOR:
                    row.append(f"{code}{ch}{C.RST}")
                else:
                    row.append(ch)
        out.append("".join(row))
    return out


def _plain(s):
    """ANSI 코드 제거 후 순수 길이(표시 폭) 계산."""
    import re as _re
    return len(_re.sub(r"\x1b\[[0-9;]*m", "", s))


def box_panel(inner_lines, indent=2, title=None):
    """뉴1 스타일 둥근 박스 패널. inner_lines는 이미 색칠된 문자열 리스트."""
    if isinstance(inner_lines, str):
        inner_lines = [inner_lines]
    content_w = max([_plain(l) for l in inner_lines] + ([_plain(title) + 4] if title else [0]))
    width = content_w + 2                 # 좌우 패딩 1칸씩
    width = max(width, 22)
    pad = " " * indent

    if title:
        # 상단: /---- title ----\
        seg = pad + _BOX_TL + _BOX_H * 2 + " " + title + " "
        top = seg + _BOX_H * max(1, width - (_plain(seg) - indent - len(pad) + 2)) + _BOX_TR
    else:
        top = pad + _BOX_TL + _BOX_H * max(2, width - 2) + _BOX_TR

    body = []
    if title:
        body.append(top)
    else:
        body.append(top)
    for ln in inner_lines:
        pad_len = width - _plain(ln)
        body.append(pad + _BOX_V + " " + ln + " " * max(0, pad_len - 2) + _BOX_V)
    bottom = pad + _BOX_BL + _BOX_H * max(2, width - 2) + _BOX_BR
    body.append(bottom)
    return body


def dotted_panel(title_lines, rows, indent=2, title_color=C.CY):
    """뉴2 스타일: 제목 행 + 점선 리더(dotted leader) 행들.

    title_lines : 배너 문자열 (Attack Details |  /  Target Details |)
    rows        : list of (label, value_label, value)  -- value_label=(색상)
    """
    if isinstance(title_lines, str):
        title_lines = [title_lines]
    max_lab = max([_plain(l) for l in title_lines] + [len(r[0]) for r in rows], default=10)
    total_w = max_lab + 26
    pad = " " * indent

    out = []
    # 제목 행
    for tl in title_lines:
        out.append(pad + paint(tl, title_color, bold=True))
    out.append("")

    for label, vcolor, value in rows:
        lead = max_lab - len(label) + 2
        leader = "." * max(6, lead)
        line = ("· " + paint(label, C.W) + " " +
                paint(leader, C.DIM) + "  " +
                paint(f"[ {value} ]", vcolor, bold=True))
        out.append(pad + line)
    return out


def show_main_screen(intro=None):
    """메인 아트 배너 + 타이틀.

    intro=None : 자동 (첫 진입엔 긴 폭포, 복귀 시엔 짧은 폭포)
    intro=숫자 : 해당 초만큼 폭포를 강제 재생
    intro=0    : 폭포 없이 배너만
    """
    global _RAIN_PLAYED, _BOOT_SHOWN

    if intro is None:
        secs = RAIN_FIRST_SEC if not _RAIN_PLAYED else RAIN_REPEAT_SEC
        _RAIN_PLAYED = True
    else:
        secs = intro

    # 1) 화면 전체에 글자가 좌르륵 쏟아지는 폭포 연출
    matrix_rain(secs)

    # 2) 배너 + 타이틀 렌더링
    clear_screen()
    banner = banner_rainbow(MAIN_ART)

    # 상단 아트 : 한 줄씩 빠르게 흘리기
    for ln in banner:
        typewrite(ln, delay=0.0012)
    time.sleep(0.08)

    # 태그라인
    tag = "=>>  RAIN  DISTRIBUTED  DENIAL-OF-SERVICE  ATTACK  ENGINE  <<="
    print(paint(" " * max(0, (term_width() - len(tag)) // 2 - 8) + tag, C.R, bold=True))
    line2 = f"  {_VERSION}   |   {_METHOD_COUNT} ATTACK METHODS   |   AUTHORIZED SECURITY TESTING ONLY"
    print(paint(" " * max(0, (term_width() - len(line2)) // 2 - 8) + line2, C.CY))

    # 3) 최초 진입 시에만 부팅 스트림 라인 (C2 패널 느낌)
    if not _BOOT_SHOWN:
        _BOOT_SHOWN = True
        print("")
        label_w = 44
        for label, status in _BOOT_LINES:
            typewrite(paint("  " + label, C.W), delay=0.001, end="")
            typewrite(paint("." * max(0, label_w - len(label)) + " ", C.DIM),
                      delay=0.0006, end="")
            typewrite(paint(status, C.G, bold=True), delay=0.0015)
            time.sleep(0.06)
        typewrite(paint("  ALL SYSTEMS READY  --  STAND BY FOR ORDERS", C.DIM),
                  delay=0.0012)
        time.sleep(0.1)
    print("")


def open_screen(art, header, sub=None):
    """옵션 진입 화면 : 화면을 지우고 전용 아트 + 헤더를 크게 연출한다."""
    clear_screen()
    print("")
    for ln in banner_rainbow(art):
        typewrite(ln, delay=0.0012)
    time.sleep(0.08)
    bar = "=" * 56
    print(paint(bar, C.DIM))
    typewrite(paint("  " + header, C.W, bold=True), delay=0.002)
    if sub:
        typewrite(paint("  " + sub, C.CY), delay=0.002)
    print(paint(bar, C.DIM))
    print("")

# ---------------------------------------------------------------------------
# 공격 시작 연출
# ---------------------------------------------------------------------------
_LAYER7_LABEL = {
    "GET": "HTTP GET FLOOD", "POST": "HTTP POST FLOOD",
    "HEAD": "HTTP HEAD FLOOD", "NULL": "NULL USER-AGENT FLOOD",
    "COOKIE": "COOKIE STORM", "OVH": "OVH BYPASS",
    "CFB": "CLOUDFLARE BYPASS", "CFBUAM": "CLOUDFLARE UAM BYPASS",
    "BYPASS": "BYPASS", "DGB": "DDoS-GUARD BYPASS",
    "AVB": "AV BYPASS", "GSB": "GSE BYPASS",
    "PPS": "PPS FLOOD", "EVEN": "EVEN FLOOD",
    "STRESS": "STRESS FLOOD", "DYN": "RANDOM SUBDOMAIN FLOOD",
    "SLOW": "SLOWLORIS", "APACHE": "APACHE FLOOD",
    "XMLRPC": "XML-RPC FLOOD", "BOT": "BOT FLOOD",
    "BOMB": "BOMBARDIER", "DOWNLOADER": "SLOW DOWNLOADER",
    "KILLER": "KILLER FLOOD", "TOR": "TOR FLOOD",
    "RHEX": "RANDOM HEX FLOOD", "STOMP": "STOMP / CAPTCHA BYPASS",
}


def _layer_label(method):
    return _LAYER7_LABEL.get(method.upper(), method)


def show_attack_start(method, target, address, port, threads, duration,
                      is_layer7=True, proxy_count=0):
    """
    공격 발사 직전 '무기 장전 + 타겟 정보' 연출을 문단별로 흘려보낸다.
    """
    layer = "LAYER-7 / HTTP FLOOD" if is_layer7 else "LAYER-4 / NETWORK FLOOD"
    method_disp = method.upper()

    paragraphs = [
        # 문단 1 : 타겟 정보
        [paint("[TARGET-SYSTEM]", C.CY, bold=True),
         "",
         paint(f"  HOST     : {target}", C.W),
         paint(f"  ADDRESS  : {address}", C.W),
         paint(f"  PORT     : {port or 80}", C.W)],
        # 문단 2 : 공격 설정
        [paint("[ATTACK-PROFILE]", C.Y, bold=True),
         "",
         paint(f"  METHOD   : {method_disp:<10} ({layer})", C.Y),
         paint(f"  THREADS  : {threads:,}", C.Y),
         paint(f"  DURATION : {duration} SEC", C.Y),
         paint(f"  PROXY    : {proxy_count:,} ACTIVE" if proxy_count else
               f"  PROXY    : NONE (DIRECT)", C.Y)],
    ]

    # 문단 1 : 화면을 정리하고 대형 ATTACK 아트를 전체에 연출
    clear_screen()
    print("")
    for ln in banner_rainbow(ATTACK_ART, color_cycle=[C.R, C.Y, C.R, C.W]):
        typewrite(ln, delay=0.0018)
    time.sleep(0.1)

    # 문단 2 : 타겟 / 설정 요약을 문단별로 조르륵
    pour(paragraphs, para_gap=0.22, char_delay=0.0045)

    # 문단 3 : 장전/기동 연출
    steps = [
        "[>] ARMING PACKET ENGINE ............ " + paint("OK", C.G, bold=True),
        "[>] LOADING PAYLOAD MAGAZINES ....... " + paint("OK", C.G, bold=True),
        "[>] WARMING UP CONNECTION POOL ...... " + paint("OK", C.G, bold=True),
        f"[>] SPINNING UP THREAD ARMY ........ {threads:,} UNITS " + paint("DEPLOYED", C.G, bold=True),
        "[>] SYNCHRONIZING FIRE CONTROL ...... " + paint("LOCKED", C.G, bold=True),
    ]
    for st in steps:
        typewrite(paint("  ", C.R) + st, delay=0.006)
    time.sleep(0.1)

    print(paint("  ********  ALL ENGINES ENGAGED  --  UNLEASH THE STORM  ********", C.R, bold=True))
    print("", flush=True)
    time.sleep(0.2)


# ---------------------------------------------------------------------------
# 실시간 상태바
# ---------------------------------------------------------------------------
_SPIN = ("-", "\\", "|", "/")


def _human_unit(num, suffix):
    for unit in ("", "K", "M", "G", "T", "P"):
        if num < 1000:
            return f"{num:.1f} {unit}{suffix}"
        num /= 1000.0
    return f"{num:.1f} E{suffix}"


def human_bps(num):
    """BPS 표기 간소화."""
    return _human_unit(num, "B/s").replace(" B/s", " B/s")


def human_size(num):
    """바이트 합계 표기."""
    return _human_unit(num, "B").replace("B/s", "B") if False else \
        _human_unit(num, "B").replace(" B", " B")


def human_bytes(num):
    """전송량 합계 표기 (B/KB/MB/GB)."""
    return _human_unit(num, "B").replace("KB", "KB")


def human_pps(num):
    """PPS 표기 간소화."""
    for unit in ("", "k", "M", "G"):
        if num < 1000:
            return f"{num:.1f}{unit}"
        num /= 1000.0
    return f"{num:.1f}T"


def _wide_ok():
    """현재 stdout 인코딩으로 █ ░ 블록 문자를 쓸 수 있는지 검사."""
    try:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        "\u2588\u2591".encode(enc)
        return True
    except Exception:
        return False


def render_status(step, total_steps, method, target, pps, bps, threads,
                  elapsed, duration):
    """1초마다 갱신되는 단일 라인 진행 상태바."""
    pct = min(100.0, max(0.0, elapsed / max(duration, 1) * 100.0))
    bar_w = 18
    filled = int(round(pct / 100.0 * bar_w))
    if _wide_ok():
        bar = "\u2588" * filled + "\u2591" * (bar_w - filled)   # █ ░
    else:
        bar = "#" * filled + "-" * (bar_w - filled)             # ASCII fallback

    spin = _SPIN[step % len(_SPIN)]
    info = (f"{paint('[' + spin + ']', C.M)}"
            f"{paint(' ' + method.upper(), C.CY, bold=True)}"
            f"{paint(' ' + target[:40], C.W)}"
            f"{paint('  [' + bar + ']', C.G)}"
            f"{paint(f' {pct:5.1f}%', C.Y)}"
            f"{paint(f' PPS {human_pps(pps):>8}', C.CY)}"
            f"{paint(f' BPS {human_bps(bps):>10}', C.M)}"
            f"{paint(f' {elapsed:>4}s/{duration}s', C.W)}"
            f"{paint(f' T:{threads}', C.DIM)}")

    width = min(term_width() - 1, 100)
    pad = max(0, width - _plain_len(info))
    try:
        print("\r" + info + " " * pad, end="", flush=True)
    except UnicodeEncodeError:
        plain = (f"\r[{spin}] {method.upper()} {target[:30]} "
                 f"[{bar}] {pct:5.1f}% PPS {pps} BPS {bps} "
                 f"{elapsed}s/{duration}s T:{threads}")
        print(plain + " " * max(0, width - len(plain)), end="", flush=True)


def _plain_len(styled):
    """ANSI 코드를 제거한 순수 길이 계산."""
    import re as _re
    return len(_re.sub(r"\x1b\[[0-9;]*m", "", styled))


# ---------------------------------------------------------------------------
# 공격 종료 연출
# ---------------------------------------------------------------------------
def show_attack_end(total_requests, total_bytes):
    """종료 후 화면을 정리하고 대형 FINISH 아트 + 통계 요약을 연출."""
    clear_screen()
    print("")
    for ln in banner_rainbow(FINISH_ART, color_cycle=[C.G, C.CY, C.G, C.W]):
        typewrite(ln, delay=0.0025)
    time.sleep(0.1)
    print(paint("  ********  ALL ENGINES HALTED  --  ATTACK MISSION COMPLETE  ********", C.G, bold=True))
    print("")

    summary = [
        f"[+] FIRE CONTROL        : ALL ENGINES HALTED",
        f"[+] TOTAL PACKETS SENT  : {total_requests:,}",
        f"[+] TOTAL BYTES DEPLOYED: {human_bytes(total_bytes) if total_bytes else '0 B'}",
        f"[+] MISSION STATUS      : COMPLETE",
    ]
    for st in summary:
        typewrite(paint(st, C.G), delay=0.008)
    print("", flush=True)


# ---------------------------------------------------------------------------
# 대화형 메인 메뉴
# ---------------------------------------------------------------------------
def _ask(prompt_text, default=None):
    """기본값이 있으면 엔터로 그대로."""
    if default is not None:
        prompt_text = f"{prompt_text} [{default}] "
    try:
        val = input(prompt_text).strip()
    except (EOFError, KeyboardInterrupt):
        print("")
        raise SystemExit(0)
    return val if val else (default if default is not None else "")


def _ask_int(prompt_text, default, minimum=1, maximum=None):
    """정수 입력 검증 프롬프트. 잘못된 값이면 다시 물어본다.
    MENU / BACK / Q / EXIT 입력 시 None 을 돌려 호출부에서 취소 처리한다."""
    if default is not None:
        prompt_text = f"{prompt_text} [{default}] "
    while True:
        try:
            raw = input(prompt_text).strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            raise SystemExit(0)
        if not raw:
            raw = default
        up = raw.upper()
        if up in {"MENU", "BACK", "Q", "EXIT", "CANCEL", "X"}:
            return None
        try:
            val = int(up)
        except ValueError:
            print(paint(f"[!] 숫자만 입력하세요. (예: {default})", C.R))
            continue
        if val < minimum:
            print(paint(f"[!] {minimum} 이상이어야 합니다.", C.R))
            continue
        if maximum is not None and val > maximum:
            print(paint(f"[!] {maximum} 이하여야 합니다.", C.R))
            continue
        return val


def _ask_required(prompt_text, err_msg):
    """빈 값이면 err_msg 를 출력하고 같은 질문을 다시 물어본다.
    MENU / BACK / Q / EXIT 입력 시 None 을 돌려 호출부에서 취소 처리한다."""
    while True:
        try:
            val = input(prompt_text).strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            raise SystemExit(0)
        if not val:
            print(paint(f"[!] {err_msg}", C.R))
            continue
        if val.upper() in {"MENU", "BACK", "Q", "EXIT", "CANCEL", "X"}:
            return None
        return val


def _run_attack(script, argv_args):
    """start.py 를 서브프로세스로 실행 (메인 화면은 다시 안 띄움)."""
    print("")
    typewrite(paint("[i] EXECUTING ATTACK MODULE .........", C.CY), delay=0.003)
    typewrite(paint("OK", C.G, bold=True), delay=0.01)
    print("", flush=True)
    try:
        subprocess.run([sys.executable, script] + argv_args, check=False)
    except KeyboardInterrupt:
        print("")
        typewrite(paint("[!] ATTACK INTERRUPTED BY OPERATOR", C.Y), delay=0.004)
    except Exception as exc:
        print(paint(f"[!] LAUNCH FAILED : {exc}", C.R, bold=True))


def wizard_layer7(script, methods):
    open_screen(LAYER7_ART, "LAYER-7  WEB FLOOD  (웹 공격 마법사)",
                "GET / POST / OVH / CFB / DYN / SLOW / RHEX ... 공격 설정")
    methods = sorted(methods)
    if len(methods) > 1:
        print(paint("  METHODS : " + ", ".join(methods), C.DIM))
        print("")
    default_method = "GET" if "GET" in methods else methods[0]
    while True:
        method = _ask("METHOD (기본 " + default_method + ")", default_method).upper() or default_method
        if method in {"MENU", "BACK", "Q", "EXIT", "CANCEL", "X"}:
            return
        if method in methods:
            break
        print(paint(f"[!] 알 수 없는 메소드: {method}  (위 METHODS 목록에서 골라주세요)", C.R))

    url = _ask_required("TARGET URL  (예: https://example.com)", "타겟 URL 이 필요합니다.")
    if url is None:
        return
    if not url.lower().startswith("http"):
        url = "http://" + url

    while True:
        socks = _ask("SOCKS TYPE  0=ALL 1=HTTP 4=SOCKS4 5=SOCKS5 (기본 1)", "1").strip()
        if not socks:
            socks = "1"
        if socks.upper() in {"MENU", "BACK", "Q", "EXIT", "CANCEL", "X"}:
            return
        if socks in {"0", "1", "4", "5", "6"}:
            break
        print(paint("[!] SOCKS TYPE 은 0, 1, 4, 5, 6 중 하나만 입력하세요.", C.R))

    threads = _ask_int("THREADS  (스레드 수, 기본 300)", "300", minimum=1)
    if threads is None:
        return
    rpc = _ask_int("RPC  (연결당 요청 수, 기본 1)", "1", minimum=1)
    if rpc is None:
        return
    proxylist = _ask("PROXY LIST  (파일명, 기본 http.txt)", "http.txt").strip()
    if not proxylist:
        proxylist = "http.txt"
    if proxylist.upper() in {"MENU", "BACK", "Q", "EXIT", "CANCEL", "X"}:
        return
    if "/" not in proxylist and not proxylist.lower().endswith(".txt"):
        proxylist += ".txt"
    duration = _ask_int("DURATION  (공격 시간 초, 기본 60)", "60", minimum=1)
    if duration is None:
        return

    print("")
    pour([
        [paint("[공격 설정 확인]", C.Y, bold=True),
         paint(f"  METHOD    : {method}", C.W),
         paint(f"  TARGET    : {url}", C.W),
         paint(f"  SOCKS     : {socks}    THREADS : {threads}", C.W),
         paint(f"  RPC       : {rpc}    PROXY   : {proxylist}", C.W),
         paint(f"  DURATION  : {duration} 초", C.W)],
    ], para_gap=0.0, char_delay=0.004)
    go = _ask("ENTER 로 공격 시작, C 입력 시 취소", "").upper()
    if go in {"C", "CANCEL", "X", "NO"}:
        return
    _run_attack(script, [method, url, socks, str(threads), proxylist, str(rpc), str(duration)])


def wizard_layer4(script, methods):
    open_screen(LAYER4_ART, "LAYER-4  NETWORK FLOOD  (서버 공격 마법사)",
                "TCP / UDP / SYN / ICMP / NTP / DNS / MEM / RDP 공격 설정")
    methods = sorted(methods)
    print(paint("  METHODS : " + ", ".join(methods), C.DIM))
    print("")
    default_method = "TCP" if "TCP" in methods else methods[0]
    while True:
        method = _ask("METHOD (기본 " + default_method + ")", default_method).upper() or default_method
        if method in {"MENU", "BACK", "Q", "EXIT", "CANCEL", "X"}:
            return
        if method in methods:
            break
        print(paint(f"[!] 알 수 없는 메소드: {method}  (위 METHODS 목록에서 골라주세요)", C.R))

    target = _ask_required("TARGET IP:PORT  (예: 1.2.3.4:80)", "타겟 IP:PORT 가 필요합니다.")
    if target is None:
        return
    if ":" not in target:
        target += ":80"
    threads = _ask_int("THREADS  (기본 500)", "500", minimum=1)
    if threads is None:
        return
    duration = _ask_int("DURATION  (초, 기본 60)", "60", minimum=1)
    if duration is None:
        return

    print("")
    pour([
        [paint("[공격 설정 확인]", C.Y, bold=True),
         paint(f"  METHOD    : {method}", C.W),
         paint(f"  TARGET    : {target}", C.W),
         paint(f"  THREADS   : {threads}", C.W),
         paint(f"  DURATION  : {duration} 초", C.W)],
    ], para_gap=0.0, char_delay=0.004)
    go = _ask("ENTER 로 공격 시작, C 입력 시 취소", "").upper()
    if go in {"C", "CANCEL", "X", "NO"}:
        return
    _run_attack(script, [method, target, str(threads), str(duration)])


def expert_cmd(script, l7, l4):
    open_screen(EXPERT_ART, "EXPERT  (명령어 직접 실행)",
                "L7 / L4 인자를 한 줄로 직접 입력하는 고급 콘솔")
    pour([
        ["  L7 :  METHOD URL SOCKS THREADS PROXYLIST RPC DURATION",
         "        예) GET https://example.com 1 300 http.txt 1 60"],
        ["  L4 :  METHOD IP:PORT THREADS DURATION",
         "        예) UDP 1.2.3.4:53 200 60"],
        ["  BACK / MENU 로 돌아가기"],
    ], para_gap=0.1, char_delay=0.003)
    line = _ask("RAIN# ")
    if not line or line.upper() in {"BACK", "MENU", "EXIT", "Q"}:
        return
    parts = line.split()
    if not parts:
        return
    method = parts[0].upper()
    if method in l7:
        need = 7
    elif method in l4:
        need = 3
    else:
        print(paint(f"[!] 알 수 없는 메소드: {method}", C.R))
        return
    if len(parts) < need:
        print(paint(f"[!] 인자가 부족합니다. (필요: {need}개, 입력: {len(parts)}개)", C.R))
        return
    if method in l7 and not parts[1].lower().startswith("http"):
        parts[1] = "http://" + parts[1]
    if method in l4 and ":" not in parts[1]:
        parts[1] += ":80"
    # 잘못된 숫자 인자를 그대로 넘기면 하위 프로세스에서 오류가 나므로 미리 검사
    try:
        if method in l7:
            socks_t = parts[2]
            if socks_t not in {"0", "1", "4", "5", "6"}:
                raise ValueError("SOCKS TYPE 은 0,1,4,5,6 중 하나")
            int(parts[3])                  # threads
            int(parts[5])                  # rpc
            if int(parts[6]) < 1:          # duration
                raise ValueError("DURATION 은 1 이상이어야 합니다")
        else:
            int(parts[2])                  # threads
            if int(parts[3]) < 1:          # duration
                raise ValueError("DURATION 은 1 이상이어야 합니다")
    except (ValueError, IndexError) as exc:
        print(paint(f"[!] 인자 오류 : {exc}  (숫자 위치 재확인 필요)", C.R))
        return
    _run_attack(script, parts)


def show_all_methods(l7, l4):
    open_screen(METHODS_ART, "ALL ATTACK METHODS  --  공격 방법 전체 보기",
                "LAYER-7 (WEB) + LAYER-4 (NETWORK) 전체 목록")
    col = 5
    for label, methods in (("LAYER-7 (WEB)", sorted(l7)), ("LAYER-4 (NETWORK)", sorted(l4))):
        print(paint(f"  [{label}]", C.Y, bold=True))
        rows = [methods[i:i + col] for i in range(0, len(methods), col)]
        for row in rows:
            typewrite("   " + "   ".join(f"{m:<12}" for m in row), delay=0.001)
        print("")
    pour([
        ["  TOOLS 메소드 : INFO  DNS  PING  CHECK  DSTAT  TSSRV  CFIP",
         "  특수 명령    : TOOLS(콘솔)  HELP  STOP"],
    ], para_gap=0.05, char_delay=0.002)


def interactive_main(l7_methods, l4_methods, script):
    """start.py 를 인자 없이 실행했을 때의 메인 화면 루프."""
    init()
    if not l7_methods:
        l7_methods = ["GET", "POST", "OVH", "CFB", "DYN", "SLOW", "RHEX", "STOMP",
                      "STRESS", "BYPASS", "PPS", "BOMB", "DOWNLOADER"]
    if not l4_methods:
        l4_methods = ["TCP", "UDP", "SYN", "ICMP", "NTP", "DNS", "MEM", "RDP"]

    l7 = set(l7_methods)
    l4 = set(l4_methods)

    while True:
        show_main_screen()
        menu = [
            paint("  RAIN  MAIN SCREEN", C.W, bold=True),
            "",
            paint("   [1] ", C.CY, bold=True) + paint("LAYER-7  웹 공격 시작  (GET / POST / OVH / CFB ...)", C.W),
            paint("   [2] ", C.CY, bold=True) + paint("LAYER-4  네트워크 공격 시작  (TCP / UDP / SYN / NTP ...)", C.W),
            paint("   [3] ", C.CY, bold=True) + paint("TOOLS  도구 콘솔  (INFO / DNS / PING / CHECK / DSTAT)", C.W),
            paint("   [4] ", C.CY, bold=True) + paint("공격 방법 전체 보기 (ALL METHODS)", C.W),
            paint("   [5] ", C.CY, bold=True) + paint("EXPERT  명령어 직접 실행", C.W),
            paint("   [0] ", C.CY, bold=True) + paint("EXIT  종료", C.W),
        ]
        pour([menu], para_gap=0.0, char_delay=0.0012)
        print("")

        try:
            choice = input(paint("  RAIN> ", C.M, bold=True)).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("")
            break

        if choice in {"0", "exit", "quit", "q", "e", "x", "종료"}:
            typewrite(paint("[!] SHUTTING DOWN ...", C.Y), delay=0.005)
            break

        try:
            if choice == "1":
                wizard_layer7(script, sorted(l7))
            elif choice == "2":
                wizard_layer4(script, sorted(l4))
            elif choice == "3":
                open_screen(TOOLS_ART, "TOOLS  도구 콘솔",
                            "INFO / DNS / PING / CHECK / DSTAT / TSSRV / CFIP")
                _run_attack(script, ["TOOLS"])
            elif choice == "4":
                show_all_methods(l7, l4)
            elif choice == "5":
                expert_cmd(script, l7, l4)
            elif choice in {"help", "h", "?", "도움"}:
                show_all_methods(l7, l4)
            else:
                print(paint(f"  [!] 알 수 없는 명령 : {choice}   (0~5 입력)", C.R))
        except Exception as exc:
            print(paint(f"  [!] 예기치 못한 오류 발생 : {exc}", C.R, bold=True))

        typewrite(paint("\n  [i] ENTER 를 누르면 메인 화면으로 돌아갑니다 ...", C.DIM), delay=0.002)
        try:
            input("")
        except (EOFError, KeyboardInterrupt):
            print("")
            break


# ---------------------------------------------------------------------------
# 단독 실행 : 연출 미리보기 데모
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init()
    show_main_screen()
    print("")  # tagline 아래 여백
    pour([
        [paint("[DEMO] RAIN 아트 엔진 미리보기", C.W, bold=True)],
        [paint("  이 화면은 start.py 를 인자 없이 실행하면 나오는 메인 메뉴입니다.", C.CY),
         paint("  아래는 공격 실행 시의 '문단별 조르륵' 연출 예시입니다.", C.CY)],
    ], para_gap=0.18, char_delay=0.004)
    show_attack_start(
        method="GET", target="example.com", address="93.184.216.34",
        port=443, threads=300, duration=60, is_layer7=True, proxy_count=1024)
    import random as _r
    try:
        for i in range(5):
            render_status(i, 60, "GET", "example.com",
                          pps=_r.randint(5000, 90000), bps=_r.randint(100000, 50000000),
                          threads=300, elapsed=i * 12 + 1, duration=60)
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    print("")
    show_attack_end(total_requests=1234567, total_bytes=987654321)
