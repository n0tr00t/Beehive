#!/usr/bin/env python
# coding : utf-8
# author : evi1m0

import random
import textwrap

one = textwrap.dedent(
      r'''
         _______                       __    __  __
        |       \                     |  \  |  \|  \
        | $$$$$$$\  ______    ______  | $$  | $$ \$$ __     __   ______
        | $$__/ $$ /      \  /      \ | $$__| $$|  \|  \   /  \ /      \
        | $$    $$|  $$$$$$\|  $$$$$$\| $$    $$| $$ \$$\ /  $$|  $$$$$$\
        | $$$$$$$\| $$    $$| $$    $$| $$$$$$$$| $$  \$$\  $$ | $$    $$
        | $$__/ $$| $$$$$$$$| $$$$$$$$| $$  | $$| $$   \$$ $$  | $$$$$$$$
        | $$    $$ \$$     \ \$$     \| $$  | $$| $$    \$$$    \$$     \
         \$$$$$$$   \$$$$$$$  \$$$$$$$ \$$   \$$ \$$     \$      \$$$$$$$
      ''')

two = textwrap.dedent(
      r'''
           ____  U _____ uU _____ u  _   _            __     __ U _____ u
        U | __")u\| ___"|/\| ___"|/ |'| |'|     ___   \ \   /"/u\| ___"|/
         \|  _ \/ |  _|"   |  _|"  /| |_| |\   |_"_|   \ \ / //  |  _|"
          | |_) | | |___   | |___  U|  _  |u    | |    /\ V /_,-.| |___
          |____/  |_____|  |_____|  |_| |_|   U/| |\u U  \_/-(_/ |_____|
         _|| \\_  <<   >>  <<   >>  //   \\.-,_|___|_,-.//       <<   >>
        (__) (__)(__) (__)(__) (__)(_") ("_)\_)-' '-(_/(__)     (__) (__)
      ''')

three = textwrap.dedent(
        r'''
                            ,;        ,;                                 ,;
          .               f#i       f#i .    .      t                  f#i
          Ef.           .E#t      .E#t  Di   Dt     Ej               .E#t
          E#Wi         i#W,      i#W,   E#i  E#i    E#, t      .DD. i#W,
          E#K#D:      L#D.      L#D.    E#t  E#t    E#t EK:   ,WK. L#D.
          E#t,E#f.  :K#Wfff;  :K#Wfff;  E#t  E#t    E#t E#t  i#D :K#Wfff;
          E#WEE##Wt i##WLLLLt i##WLLLLt E########f. E#t E#t j#f  i##WLLLLt
          E##Ei;;;;. .E#L      .E#L     E#j..K#j... E#t E#tL#i    .E#L
          E#DWWt       f#E:      f#E:   E#t  E#t    E#t E#WW,       f#E:
          E#t f#K;      ,WW;      ,WW;  E#t  E#t    E#t E#K:         ,WW;
          E#Dfff##E,     .D#;      .D#; f#t  f#t    E#t ED.           .D#;
          jLLLLLLLLL;      tt        tt  ii   ii    E#t t               tt
        ''')

four = textwrap.dedent(
        r'''
           ___                    _  _      _
          | _ )    ___     ___   | || |    (_)    __ __    ___
          | _ \   / -_)   / -_)  | __ |    | |    \ V /   / -_)
          |___/   \___|   \___|  |_||_|   _|_|_   _\_/_   \___|
        _|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|
        "`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'
        ''')

def getBanner():
    logo = [one, two, three, four]
    statistics = random.choice(logo)
    return statistics
