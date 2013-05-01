import spiff
import bonehead
from bonehead.ui import Page
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork, uic
import threading
import tempfile
import subprocess
from mako.template import Template

class SpiffResourceLabelPlugin(bonehead.Plugin):
	def newPage(self, name, args, ui):
		return SpiffResourcePage(ui)

class CertificationModel(QtCore.QAbstractListModel):
  def __init__(self, parent=None):
    super(CertificationModel, self).__init__(parent)
    self._resource = None

  def setResource(self, resource):
    self.beginResetModel()
    self._resource = resource
    self.endResetModel()

  def rowCount(self, parent):
    if self._resource is not None:
      return len(self._resource['certifications'])
    return 0

  def data(self, idx, role):
    if self._resource is not None:
      if role == QtCore.Qt.DisplayRole:
        cert = self._resource['certifications'][idx.row()]
        return "%s, %s: %s"%(cert['member']['lastName'],
            cert['member']['firstName'], cert['comment'])

class DetailModel(QtCore.QAbstractListModel):
  def __init__(self, parent=None):
    super(DetailModel, self).__init__(parent)
    self._resource = None

  def setResource(self, resource):
    self.beginResetModel()
    self._resource = resource
    self.endResetModel()

  def rowCount(self, parent):
    if self._resource is not None:
      return len(self._resource['metadata'])
    return 0
  
  def data(self, idx, role):
    if self._resource is not None:
      if role == QtCore.Qt.DisplayRole:
        meta = self._resource['metadata'][idx.row()]
        return "%s: %s"%(meta['name'], meta['value'])

class ResourceModel(QtCore.QAbstractListModel):
  ResourceRole = QtCore.Qt.UserRole
  def __init__(self, api, parent=None):
    super(ResourceModel, self).__init__(parent)
    self._api = api
    self.refresh()

  def refresh(self):
    self.beginResetModel()
    self._api.clearCache()
    self._cache = self._api.resources()
    self.endResetModel()

  def rowCount(self, parent):
    return len(self._cache)

  def data(self, idx, role):
    if role == QtCore.Qt.DisplayRole:
      return "%s: %s"%(self._cache[idx.row()].id,
          self._cache[idx.row()]['name'])
    if role == self.ResourceRole:
      return self._cache[idx.row()]

class SpiffResourcePage(Page):
  def __init__(self, ui):
    super(SpiffResourcePage, self).__init__('Resources', ui)
    self._api = spiff.API(ui.app.spaceAPI.raw['x-spiff-url'], verify=False)
    basename = '/'.join(__file__.split("/")[0:-1]+['resources.ui',])
    uic.loadUi(basename, self)
    self.model = ResourceModel(self._api, self)
    self.certModel = CertificationModel(self)
    self.filterModel = QtGui.QSortFilterProxyModel(self)
    self.filterModel.setSourceModel(self.model)
    self.filterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
    self.detailModel = DetailModel(self)
    self.resourceView.setModel(self.filterModel)
    self.detailView.setModel(self.detailModel)
    self.certificationView.setModel(self.certModel)
    self.printButton.clicked.connect(self.printLabel)
    self.refreshButton.clicked.connect(self.model.refresh)
    self.resourceView.selectionModel().currentChanged.connect(self.updateDetails)
    self.quickSearch.textChanged.connect(self.filterModel.setFilterFixedString)

  def updateDetails(self, cur, previous):
    resource = cur.data(ResourceModel.ResourceRole).toPyObject()
    self.detailModel.setResource(resource)
    self.certModel.setResource(resource)

  def printLabel(self):
    idx = self.resourceView.selectionModel().currentIndex()
    if idx.isValid():
      resource = idx.data(ResourceModel.ResourceRole).toPyObject()
      tempDir = tempfile.mkdtemp()
      tempOut = open("%s/out.latex"%(tempDir), 'w')
      tempQR = open("%s/qr.png"%(tempDir), 'w')
      tempQR.write(resource.qrCode(8))
      tempQR.close()
      template = Template(filename='resource-label.latex')
      tempOut.write(template.render(name=resource['name'], id=resource.id))
      tempOut.close()

      args = ["pdflatex", "-halt-on-error", "%s/out.latex"%(tempDir)]

      subprocess.call(args, cwd=tempDir)

      print "Wrote out.pdf to", tempDir
      #conn = cups.Connection()
      #conn.printFile(self._printer, "%s/out.pdf"%(tempDir), "Label for %s"%(resource['name']), {'PageSize':'29x90','BrMirror':'OFF', 'orientation-requested': '5'})
      self.reset()
