class ServerError(Exception):
  def __init__(self, message):
    super(ServerError, self).__init__()
    self.__msg = message

  def __str__(self):
    return self.__msg

  def __repr__(self):
    return "ServerError(%r)"%(self.__msg)

