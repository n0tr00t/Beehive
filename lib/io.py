from __future__ import print_function

import sys
import platform
import colorama

msgTypeColor = {
    None: ('', ''),
    'info': (colorama.Fore.BLUE, '[*] '),
    'warning': (colorama.Fore.YELLOW, '[!] '),
    'error': (colorama.Fore.RED, '[-] '),
    'ok': (colorama.Fore.GREEN, '[+] '),
}

def bprint(msgStr, msgType=None, vbCur=1, vbTs=1):
    '''
    print function with:
        1. diffrent message type with different color:
            info - default color
            warning - yellow
            error - red
            ok - green
        2. verbose level control.
    args:
        msgStr - the message string.
        msgType - message type(info/warning/error/ok).
        vbCur - current verbose level.
        vbTs - verbose threshold to print the message.
    '''
    if vbCur >= vbTs:
        # deprecated, because colorama.init() disables the auto-completion
        # of cmd2, although it works very well in platform auto-detection.
        #colorama.init(autoreset=True)

        if platform.system().lower() == 'windows':
            stream = colorama.AnsiToWin32(sys.stdout)
        else:
            stream = sys.stdout

        print(msgTypeColor[msgType][0] + \
                  colorama.Style.BRIGHT + \
                  msgStr + \
                  colorama.Fore.RESET + \
                  colorama.Style.RESET_ALL,
              file=stream)

def bprintPrefix(msgStr, msgType=None, vbCur=1, vbTs=1):
    '''
    print function with:
        1. diffrent message type with different color:
            info - default color
            warning - yellow
            error - red
            ok - green
        2. verbose level control.
    args:
        msgStr - the message string.
        msgType - message type(info/warning/error/ok).
        vbCur - current verbose level.
        vbTs - verbose threshold to print the message.
    '''
    if vbCur >= vbTs:
        # deprecated, because colorama.init() disables the auto-completion
        # of cmd2, although it works very well in platform auto-detection.
        #colorama.init(autoreset=True)

        if platform.system().lower() == 'windows':
            stream = colorama.AnsiToWin32(sys.stdout)
        else:
            stream = sys.stdout

        print(msgTypeColor[msgType][0] + \
                  colorama.Style.BRIGHT + \
                  msgTypeColor[msgType][1] + \
                  colorama.Fore.RESET + \
                  colorama.Style.RESET_ALL,
              end='',
              file=stream)
        print(msgStr,
              file=stream)


if __name__ == '__main__':
    for msgType, color in msgTypeColor.iteritems():
        bprint('233333', msgType)

    for msgType, color in msgTypeColor.iteritems():
        bprintPrefix('666666', msgType)
