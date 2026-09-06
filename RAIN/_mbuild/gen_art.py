# -*- coding: utf-8 -*-
"""figlet slant 아트 생성 - 빌드 전용 도우미 (사용 후 삭제)."""
import os
import pyfiglet

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "slant"


def make(word):
    art = pyfiglet.figlet_format(word, font=FONT)
    lines = art.split("\n")
    # 끝의 빈 줄 제거, 각 줄의 끝 공백만 정리(앞 공백 유지)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def dump(name, lines):
    path = os.path.join(HERE, name + ".art.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(name, "rows=", len(lines))
    for i, ln in enumerate(lines):
        print("%2d|%s|" % (i, ln))


def main():
    dump("seojun", make("seojun"))
    dump("attack", make("attack"))
    dump("complete", make("complete"))


if __name__ == "__main__":
    main()
