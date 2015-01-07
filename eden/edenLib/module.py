from .node import *
from .util import *
from .store import *

class Module:
	topLevel = True

	def __init__ (self, moduleName = None, nodeStoreName = defaultNodeStoreName):
		self.topLevel = Module.topLevel
		Module.topLevel = False
		
		self.modules = []
		self.moduleName = moduleName if moduleName else decapitalize (self.__class__.__name__)
		setattr (app, self.moduleName, self)
				
		if self.topLevel:
			if nodeStoreName:
				app.nodeStore = Store (nodeStoreName)
				
			self.defineParts ()

	def addModule (self, module):
		module.defineModules ()
		self.modules.append (module)
		return module
		
	def defineModules (self):
		pass
		
	def callRecursively (self, definerName):
		if hasattr (self, definerName):
			getattr (self, definerName) ()

		for module in self.modules:
			module.callRecursively (definerName)

	def defineParts (self):
		self.defineModules ()
		self.callRecursively ('defineNodes')
		self.callRecursively ('defineExceptions')
		self.callRecursively ('defineDependencies')
		self.callRecursively ('getView')
		self.callRecursively ('defineActions')
		currentEvent.getNext ()	# Terminate initialisation, so that Node.touched will work at loading a store
		
	def getView (self):
		if not hasattr (self, 'view'):
			self.view = self.defineViews ()
			
		return self.view
		
	def addNode (self, node, name, store = None, nodeKey = ''):
		setattr (self, name, node)
						
		if not store is None:
			if nodeKey == '':
				nodeKey = name
				
			store.add (node, self.moduleName + '.' + nodeKey)
			
		return node
		
	def execute (self,):
		if self.topLevel:
			if hasattr (app, 'nodeStore'):
				app.nodeStore.load ()
							
			self.getView () .execute ()
			
			if hasattr (app, 'nodeStore'):
				app.nodeStore.save ()
