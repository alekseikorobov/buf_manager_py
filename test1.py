#!/usr/bin/env python
# https://stackoverflow.com/questions/74838210/how-to-get-and-set-non-standard-formats-to-clipboard-using-python-win32clipboar
import sys
from pprint import pprint as pp

import win32gui as wgui
import win32clipboard as wcb
import win32con as wcon


def clipboard_formats():
    l = [wcb.EnumClipboardFormats(0)]
    while l[-1]:
        l.append(wcb.EnumClipboardFormats(l[-1]))
    l.pop()
    ret = {}
    for e in l:
        try:
            name = wcb.GetClipboardFormatName(e)
        except:
            name = ""
        ret[e] = name
    return ret


def is_simple_format(fmt):  # @TODO: dummy!!!
    return fmt in (
        wcon.CF_TEXT,
        wcon.CF_OEMTEXT,
        wcon.CF_UNICODETEXT,
        wcon.CF_LOCALE
    )


def main(*argv):
    try:
        hwnd = int(argv[0])
    except (IndexError, ValueError):
        hwnd = None
    print("Handling clipboard for window: {:} ({:s})".format(hwnd, wgui.GetWindowText(hwnd or wgui.GetActiveWindow())))
    clip = wcb.OpenClipboard(hwnd)
    fmts_dict = clipboard_formats()
    print("Available formats:")
    pp(fmts_dict, sort_dicts=0)
    try:
        fmt = int(argv[1])
        fmts_dict[fmt]
    except (IndexError, ValueError, KeyError):
        fmt = tuple(fmts_dict.keys())[0]  # 1st one
    print("Using format {:d} ({:s})".format(fmt, fmts_dict[fmt]))

    if is_simple_format(fmt):
        print("Handling simple (text) format data")
        data = wcb.GetClipboardData(fmt)
        print("--- Data ---\n{:}\n--- Data end ---".format(data))
    else:
        print("Handling custom format data")
        hg = wcb.GetClipboardDataHandle(fmt)
        print("HGLOBAL: {:}".format(hg))
        data = wcb.GetGlobalMemory(hg)
        data_len = getattr(data, "__len__", lambda: -1)()
        print("Data length: {:d}".format(data_len))
        if data_len < 0x100:
            print("--- Data ---\n{:}\n--- Data end ---".format(data))

    wcb.EmptyClipboard()
    wcb.SetClipboardData(fmt, data)

    wcb.CloseClipboard()


if __name__ == "__main__":
    print("Python {:s} {:03d}bit on {:s}\n".format(" ".join(elem.strip() for elem in sys.version.split("\n")),
                                                   64 if sys.maxsize > 0x100000000 else 32, sys.platform))
    rc = main(*sys.argv[1:])
    print("\nDone.\n")
    sys.exit(rc)