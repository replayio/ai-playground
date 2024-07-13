import time

def formatSecondsDelta(start: float):
  return f'{round(time.time() - start, 2)}s'
