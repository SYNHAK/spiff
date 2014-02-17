import logging
import inspect

def funcLog():
  frame = inspect.stack()[1]
  localVars = frame[0].f_locals
  if 'self' in localVars:
    logName = '%s.%s.%s'%(localVars['self'].__class__.__module__, localVars['self'].__class__.__name__, frame[3])
  else:
    logName = '%s.%s'%(frame[0].f_globals['__name__'], frame[3])
  return logging.getLogger(logName)
