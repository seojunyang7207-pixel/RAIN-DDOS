# -*- coding: utf-8 -*-
"""
ddos_art - SEOJUN 아트 엔진 (MH-DDoS fork UI 리브랜드 버전)
================================================================
start.py 의 화면/연출 전담 모듈. 아래 공개 API 는 기존 버전과 완전히
호환되도록 유지한다.

  init() / is_color() / paint() / clear_screen() / typewrite()
  cascade() / pour() / term_width() / matrix_rain()
  show_main_screen() / show_attack_start() / render_status()
  show_attack_end() / interactive_main()
  wizard_layer7() / wizard_layer4() / expert_cmd() / show_all_methods()
  human_bps() / human_size() / human_bytes() / human_pps()
  display_name()
  C / RAINBOW
  _VERSION / _METHOD_COUNT / RAIN_FIRST_SEC / RAIN_REPEAT_SEC

브랜드: fancy 글꼴 "𝓈ℯℴ𝒿𝓊𝓃" (유니코드 수학 알파벳), 콘솔 환경에서
표현이 불가능하면 ASCII 폴백 "SEOJUN" 을 사용한다.
"""

import ctypes
import os
import random
import re
import shutil
import subprocess
import sys
import time
import unicodedata

# ---------------------------------------------------------------------------
# 색상 / 상수
# ---------------------------------------------------------------------------


class C:
    """ANSI 색상/스타일 코드."""
    RST = "\x1b[0m"
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    R = "\x1b[91m"    # 밝은 빨강
    G = "\x1b[92m"    # 밝은 초록
    Y = "\x1b[93m"    # 밝은 노랑
    B = "\x1b[94m"    # 밝은 파랑
    M = "\x1b[95m"    # 밝은 마젠타
    CY = "\x1b[96m"   # 밝은 청록
    W = "\x1b[97m"    # 밝은 흰색


RAINBOW = [C.M, C.CY, C.W, C.CY, C.G, C.Y, C.R, C.M]

# 브랜드 이름 (fancy / plain)
NAME = "𝓈ℯℴ𝒿𝓊𝓃"
PLAIN_NAME = "SEOJUN"

_VERSION = "v2.4 SNAPSHOT"
_METHOD_COUNT = "56+"

# 매트릭스 레인 기본 타이밍
RAIN_FIRST_SEC = 2.6     # 최초 메인 화면 진입 시
RAIN_REPEAT_SEC = 1.1    # 메뉴에서 복귀할 때마다
RAIN_CHARS = "アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789ABCDEF"

_SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
_SPIN_FALLBACK = "|/-\\"

_RAIN_PLAYED = False     # 레인을 한 번이라도 재생했는지
_BOOT_SHOWN = False      # 부팅 로그를 한 번이라도 출력했는지
_L7_PREVIEW = "GET / POST / OVH / CFB / DYN"  # 메뉴 [1] 미리보기용

_INIT_DONE = False
_COLOR = False           # VT/ANSI 지원 여부 (init 에서 결정)
_FANCY = False           # fancy 브랜드명 사용 여부 (init 에서 결정)


# ---------------------------------------------------------------------------
# 내부 유틸
# ---------------------------------------------------------------------------

def _is_tty(stream=None):
    """stdout(또는 지정 스트림)이 터미널인지 안전하게 검사."""
    s = stream if stream is not None else sys.stdout
    try:
        return bool(s.isatty())
    except Exception:
        return False


def _encodable(chars, enc=None):
    """현재 stdout 인코딩으로 chars 를 표현할 수 있는지."""
    enc = enc or getattr(sys.stdout, "encoding", None)
    if not enc:
        return True
    try:
        chars.encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def _pick(glyph, fallback):
    """표현 불가능한 글리프면 폴백 문자 반환. (» -> >, · -> - 등)"""
    return glyph if _encodable(glyph) else fallback


def _sep():
    """메뉴/라벨 사이 장식 구분자 · (불가능하면 -)."""
    return _pick("·", "-")


def _arrow():
    """프롬프트 장식 화살표 » (불가능하면 >)."""
    return _pick("»", ">")


def _plain(text):
    """ANSI 시퀀스를 제거한 순수 텍스트."""
    return re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", text)


def _disp_w(text):
    """한글/전각 문자를 2칸으로 계산한 표시 폭."""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1
               for ch in text)


def _pad(text, width):
    """ANSI 코드를 무시하고 순수 표시 폭 기준 오른쪽 패딩."""
    return text + " " * max(0, width - _disp_w(_plain(text)))


def _center(text, width):
    """ANSI 코드를 무시하고 표시 폭 기준 중앙 정렬."""
    gap = max(0, width - _disp_w(_plain(text)))
    left = gap // 2
    return " " * left + text + " " * (gap - left)


def _wide_ok():
    """블록 문자(█░)를 출력할 수 있는지."""
    return _encodable("\u2588\u2591")


def _glyph_bar():
    """진행 바 문자. 불가능하면 ASCII #/- 폴백."""
    if _wide_ok():
        return "\u2588", "\u2591"
    return "#", "-"


def _ansi_strip_len(text):
    return len(_plain(text))


# ---------------------------------------------------------------------------
# 초기화 / 브랜드 이름
# ---------------------------------------------------------------------------

def _fancy_ok():
    """fancy 브랜드명 표시 조건:
    색상 지원(tty) + stdout 인코딩으로 NAME 표현 가능 + (Windows) CP 65001
    """
    if not _COLOR:
        return False
    if not _encodable(NAME):
        return False
    if os.name == "nt":
        try:
            if ctypes.windll.kernel32.GetConsoleOutputCP() != 65001:
                return False
        except Exception:
            return False
    return True


def init():
    """Windows 콘솔에 VT(ANSI) 처리 활성화 + 콘솔 타이틀 설정.

    멱등이며 반환값은 색상 지원 여부(불리언). display_name() 을 호출하지
    않는다(재귀 방지).
    """
    global _COLOR, _FANCY, _INIT_DONE
    if _INIT_DONE:
        return _COLOR
    _INIT_DONE = True

    if os.environ.get("NO_COLOR"):
        _COLOR = False
        _FANCY = False
        return _COLOR

    if os.name == "nt":
        try:
            k32 = ctypes.windll.kernel32
            out = k32.GetStdHandle(-11)          # STD_OUTPUT_HANDLE
            mode = ctypes.c_uint32()
            if k32.GetConsoleMode(out, ctypes.byref(mode)):
                VT = 0x0004                      # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                k32.SetConsoleMode(out, mode.value | VT)
        except Exception:
            pass

    _COLOR = bool(sys.stdout and _is_tty(sys.stdout))
    _FANCY = _fancy_ok()

    # 출력 리다이렉트(파이프/로그) 환경에서 한글 등이 인코딩 예외로
    # 죽지 않도록 오류 시 대체 문자로 출력하게 만든다.
    if not _is_tty(sys.stdout):
        try:
            sys.stdout.reconfigure(errors="replace")
        except Exception:
            pass

    if os.name == "nt":
        try:
            title = "%s - DDoS Attack Engine %s" % (
                NAME if _FANCY else PLAIN_NAME, _VERSION)
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except Exception:
            pass

    return _COLOR


def display_name():
    """사용자에게 보여줄 브랜드 이름. (fancy 불가 시 SEOJUN)

    호출 시점에 init() 이 안 되어 있으면 지연 초기화한다 (멱등).
    """
    init()
    return NAME if _FANCY else PLAIN_NAME


def is_color():
    return _COLOR


# ---------------------------------------------------------------------------
# 기본 출력 효과
# ---------------------------------------------------------------------------

def paint(text, code, bold=False):
    """색상 코드로 감싼 문자열 반환. 색상 미지원 시 원문 그대로."""
    if not _COLOR:
        return text
    return f"{C.BOLD if bold else ''}{code}{text}{C.RST}"


def clear_screen():
    if _COLOR:
        print("\x1b[2J\x1b[H", end="", flush=True)
    else:
        print("\n" * 3, end="", flush=True)


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
    """'문단별 조르륵' 폭포 출력.

    paragraphs: list[list[str]] (문단 -> 줄들). str 하나도 허용.
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


def banner_rainbow(art, color_cycle=None):
    """아트 각 줄에 무지개 색을 순환 입힌 리스트 반환."""
    cycle = color_cycle or RAINBOW
    lines = art.split("\n")
    out = []
    for i, ln in enumerate(lines):
        if ln.strip():
            out.append(paint(ln, cycle[i % len(cycle)], bold=True))
        else:
            out.append("")
    return out


# ---------------------------------------------------------------------------
# 디지털 문자 폭포 (레인) - '글자가 좌르륵'
# ---------------------------------------------------------------------------

def matrix_rain(seconds=RAIN_REPEAT_SEC, fps=32, cols=0, rows=0,
                head_code="\x1b[97;1m", near_code="\x1b[92m",
                dim_code="\x1b[32m"):
    """컬럼 단위 매트릭스 레인 (전체 프레임 다시 그리기 방식).

    조건: 색상 지원 + tty + seconds > 0. 파이프/리다이렉트 환경에서는
    조용히 아무것도 하지 않는다.
    """
    if seconds <= 0:
        return
    if not (_COLOR and _is_tty(sys.stdout)):
        return

    W = min(max(int(cols) if cols else term_width(), 10), 200)
    H = int(rows) if rows else (_term_wh()[1] - 2)
    H = max(8, H)

    # 컬럼 상태: head(머리 행), speed(프레임당 이동), tail(꼬리 길이)
    drops = {}

    def spawn(c):
        drops[c] = [-random.uniform(0.0, float(H)),   # 화면 위에서 시작
                    random.uniform(0.3, 1.2),          # cells/frame
                    random.randint(5, max(6, min(24, H)))]

    for c in range(W):
        if random.random() < 0.62:
            spawn(c)

    try:
        sys.stdout.write("\x1b[?25l")                 # 커서 숨김
        sys.stdout.flush()
        deadline = time.perf_counter() + max(seconds, 0.05)
        while time.perf_counter() < deadline:
            frame_start = time.perf_counter()
            # 컬럼 상태 갱신
            for c, st in list(drops.items()):
                st[0] += st[1]
                if st[0] - st[2] > H:                 # 꼬리가 화면 밖으로
                    spawn(c)                          # 새 드롭으로 재생성
            # 프레임 버퍼 조립 (전체 다시 그리기)
            buf = ["\x1b[H"]
            for y in range(H):
                row_parts = []
                for c in range(W):
                    st = drops.get(c)
                    if not st:
                        continue
                    head, _speed, tail = st
                    top = int(head)
                    if not (0 <= y <= top):
                        continue
                    bot = max(0, top - tail + 1)
                    if y < bot:
                        continue
                    dist = top - y
                    if dist <= 0:
                        code = head_code
                    elif dist <= 3:
                        code = near_code
                    else:
                        code = dim_code
                    ch = random.choice(RAIN_CHARS)
                    row_parts.append(code + ch)
                if row_parts:
                    buf.append("".join(row_parts))
                else:
                    buf.append("")
            frame = "\r\n".join(buf)
            sys.stdout.write(frame)
            sys.stdout.flush()
            # 1/fps 예산 유지
            spent = time.perf_counter() - frame_start
            sleep_for = (1.0 / max(fps, 1)) - spent
            if sleep_for > 0:
                time.sleep(sleep_for)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            sys.stdout.write("\x1b[?25h\x1b[0m")      # 커서 복원
            sys.stdout.flush()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 아트 리소스 (베이크 스크립트가 r"""...""" 로 치환)
# ---------------------------------------------------------------------------

SEOJUN_ART = __ART_SEOJUN__
ATTACK_ART = __ART_ATTACK__
COMPLETE_ART = __ART_COMPLETE__
