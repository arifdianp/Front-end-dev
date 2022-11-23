# -*- coding: utf-8 -*-
from threading import Thread

"""Postpone decorator is used to execute the function asynchronusly, as a new thread"""
def postpone(function):
  def decorator(*args, **kwargs):
    t = Thread(target = function, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
  return decorator
