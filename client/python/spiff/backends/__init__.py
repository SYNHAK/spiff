
class Backend(object):
  def get(self, uri, verify, headers, params):
    raise NotImplemented

  def post(self, uri, verify, headers, data):
    raise NotImplemented

  def patch(self, uri, verify, headers, data):
    raise NotImplemented

  def delete(self, uri, verify, headers, data):
    raise NotImplemented

  def processResponse(self, response, status, blankResponse=False):
    raise NotImplemented

def defaultBackend():
  from spiff.backends.requestsBackend import RequestsBackend
  return RequestsBackend()
