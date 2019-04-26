#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import logging.config

p_dir = os.path.dirname(__file__)
g_dir = os.path.dirname(p_dir)
# os.chdir(g_dir)

logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger('root')

