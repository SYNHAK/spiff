import requests
from spiff import backends
from spiff import errors

class RequestsBackend(backends.Backend):
  def get(self, uri, verify, headers, params):
    return requests.get(uri, verify=verify, headers=headers, params=params)

  def post(self, uri, verify, headers, data):
    return requests.post(uri, data=data, verify=verify, headers=headers)

  def patch(self, uri, verify, headers, data):
    return requests.patch(uri, data=data, verify=verify, headers=headers)

  def delete(self, uri, verify, headers, params):
    return requests.delete(uri, params=params, verify=verify, headers=headers)

  def processResponse(self, response, status, blankResponse=False):
    if response.status_code != status:
      if len(response.content):
        try:
          errorMsg = response.json()
        except ValueError:
          raise errors.ServerError(response.content)
        if 'traceback' in errorMsg:
          raise errors.ServerError(errorMsg['traceback'])
        else:
          raise errors.ServerError(str(errorMsg['error']))
      else:
        response.raise_for_status()
    if not blankResponse:
      try:
        return response.json()
      except ValueError:
        raise errors.ServerError(response.content)
    return None

