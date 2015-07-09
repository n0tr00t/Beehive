#!/usr/bin/env python
# coding: utf-8
# site  : beebeeto.com
# team  : n0tr00t security


class BeeScanBaseException(Exception):
    pass


class BeeScanLaunchException(BeeScanBaseException):
    pass


class LoadDefaultArgsException(BeeScanBaseException):
    pass
