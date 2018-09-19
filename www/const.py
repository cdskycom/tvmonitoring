# -*- coding: utf-8 -*-

class _const:
  class ConstError(TypeError): pass
  class ConstCaseError(ConstError): pass

  def __setattr__(self, name, value):
      if name in self.__dict__:
          raise self.ConstError("can't change const %s" % name)
      if not name.isupper():
          raise self.ConstCaseError('const name "%s" is not all uppercase' % name)
      self.__dict__[name] = value

const = _const()
const.STATUS_ACCEPT = 'ACCEPT'
const.STATUS_DEALING = 'DEALING'
const.STATUS_FINISHED = 'FINISHED'
const.STATUS_ALL = 'ALL'
const.TASK_PENDING = 0
const.TASK_FINISHED = 1
const.RETURN_OK = 0
