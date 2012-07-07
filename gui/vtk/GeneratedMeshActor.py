from PeacockActor import PeacockActor

import vtk
from vtk.util.colors import peacock, tomato, red, white, black

class GeneratedMeshActor(PeacockActor):
  def __init__(self, renderer, mesh):
    PeacockActor.__init__(self, renderer)
    self.mesh = mesh

    self.mapper = vtk.vtkDataSetMapper();
    self.mapper.SetInput(self.mesh);

    self.actor = vtk.vtkActor();
    self.actor.SetMapper(self.mapper);
    self.actor.GetProperty().SetPointSize(4)
    self.actor.GetProperty().SetEdgeColor(0,0,0)
    self.actor.GetProperty().SetAmbient(0.3);

  def getBounds(self):
    return self.actor.GetBounds()

  def _show(self):
    self.renderer.AddActor(self.actor)

  def _hide(self):
    self.renderer.RemoveActor(self.actor)

  def _showEdges(self):
    self.actor.GetProperty().EdgeVisibilityOn()
    
  def _hideEdges(self):
    self.actor.GetProperty().EdgeVisibilityOff()

  def _goSolid(self):
    self.actor.GetProperty().SetRepresentationToSurface()
    
  def _goWireframe(self):
    self.actor.GetProperty().SetRepresentationToWireframe()

  def _setColor(self, color):
    self.actor.GetProperty().SetColor(color)