from .node import *

class Module:
	def __init__ (self, moduleKey = '', defineParts = False):
		self.modules = []
		self.moduleKey = moduleKey
		if defineParts:
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
				
			if self.moduleKey == '':
				qualifiedKey = nodeKey
			else:
				qualifiedKey = self.moduleKey + '.' + nodeKey
				
			store.add (node, qualifiedKey)
			
		return node
