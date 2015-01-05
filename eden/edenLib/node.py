# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

import sys

from .base import *
from .util import *

currentEvent = UniqueNumber (1)
triggerNode = CallableValue ()

class Transactor:
	def __init__ (self):
		self.clear ()

	def clear (self):
		self.updatedNodes = []
	
	def add (self, node):
		self.updatedNodes.append (node)
		
	def contains (self, node):
		return node in self.updatedNodes	# Reference equality
			
	def rollBack (self):
		for node in self.updatedNodes:
			node.rollBack ()
			
	def act (self):
		for node in self.updatedNodes:
			node.act ()

transactor = Transactor ()

class Node (object):							# Node representing atomary partial state in a state machine
	def __init__ (self, *value):					# Initial value is optional, not needed in case of dependent nodes
		self.sinkNodes = []								# Nodes that depend on this node
		self.links = []									# Zero or more links to bareRead / bareWrite pairs
		self.exceptions = []
		self.actions = []
		self.validator = lambda value: True				# Validators are deprecated, use exceptions instead
		
		self.persistent = False							# Assume not worth persisting
		self.evaluating = False
		if len (value) == 1:							# If node is supposed to be freely initialized
			self.currentValue = value [0]				#	Free initialisation
			self.previousValue = self.currentValue		#	Make sure previousValue is available in case of free initialisation
			self.event = currentEvent ()				#	Remember up to date
			
			if not value [0] is None:					#	If it is a freely initialized ordinary node rather than an event-only node
				self.persistent = True					#		Remember it is part of a non-redundant basis for persistence			

		else:											# Else
			self.event = 0								#	Should be updated
			
	version = property (lambda self: self.event)
	
	def trace (self, traceName):
		self.traceName = traceName
		return self
	
	def traceNameIs (traceName):
		return hasattr (self, 'traceName') and self.traceName == traceName
		
	def printTrace (self, label, attribute):
		if hasattr (self, 'traceName') and hasattr (self, attribute):
			print label + ',', self.traceName + '.' + attribute, '==', getattr (self, attribute)

	def dependsOn (self, sourceNodes, getter = lambda: None):		# Lay dependency relations this node and other nodes that it depends on
		if hasattr (self, 'sourceNodes'):				# If dependsOn was called before for this node
			for sourceNode in self.sourceNodes:			#	For all nodes that this node depended upon previously
				sourceNode.sinkNodes.remove (self)		#		Remove the old dependency
	
		for sourceNode in sourceNodes:					# For each node that this node depends upon
			sourceNode.sinkNodes.append (self)			#	Register this node with that other node
			
		self.sourceNodes = sourceNodes					# Remember sourceNodes
			
		self.getter = getter							# Lay down how to construct the value of this node from the values of those others
		
		try:
			self.evaluate ()							# Dependent initialisation by backward evaluation
		except:												 
			pass										# Lacks some needed dependency, or getter is incomputable, wait for initialisation by forward propagation
			
		return self
		
	def addException (self, condition, aClass, message):
		self.exceptions.append ((condition, aClass, message))
		return self
		
	def addAction (self, action):	# Convenience method, mainly to allow call chaining, added y14m12d10
		self.actions.append (action)
		return self
				
	def invalidate (self):							# Invalidation phase, to know where to propagate and prevent cycles
		# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		if hasattr (self, 'currentValue'):			#		If already initialised
			if not transactor.contains (self):		#			If currentValue not already saved (prevent saving intermediate from follow)
				self.previousValue = self.currentValue	#			Remember previousValue early to enable rollBack if getter raises exception
				transactor.add (self)					#			Register that this node may alter its value as part of the current transaction
		# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

		self.event = 0									# Should be updated ??? Only if it does not have the current event number?

		for sinkNode in self.sinkNodes:					# For all nodes that depend upon this node
			if sinkNode.event != 0:						#	If not closing a cycle
				sinkNode.invalidate ()					#		Invalidate that dependent node

	def validate (self):
		for exception in self.exceptions:
			try:	# Try and except block swapped y14m12d24
				if exception [0] ():
					raise exception [1] (exception [2])
			except TypeError:						# Checkfunctions with self.currentValue parameter are deprecated
				if exception [0] (self.currentValue):
					raise exception [1] (exception [2])
	
		if not self.validator (self.currentValue):	# Validators are deprecated
			raise Error ('Node value invalid')

	def evaluate (self):							# Evaluation phase, two way propagation
		self.printTrace ('Evaluate, start', 'event')

		if self.event == 0:	# So only nodes that lay on the trigger path are REALLY ever computed!
			if self.evaluating:
				print 'Event: ', self.event
				print 'Previous value: ', self.previousValue
				print 'Current value: ', self.currentValue
				raise FatalError ('Recursive node evaluation')
			else:
				self.evaluating = True
				try:
					if hasattr (self, 'currentValue'):			#		If already initialised
#						if not transactor.contains (self):		#			If currentValue not already saved (prevent saving intermediate from follow)
#							self.previousValue = self.currentValue	#			Remember previousValue early to enable rollBack if getter raises exception
#							transactor.add (self)					#			Register that this node may alter its value as part of the current transaction
						
						self.printTrace ('Evaluate, before getter', 'currentValue')
						self.currentValue = self.getter ()		#			Compute currentValue, backpropagate if needed to evaluate getter
						self.printTrace ('Evaluate, after getter', 'currentValue')
					else:										#		If not yet initialized
						self.currentValue = self.getter ()		#			Dependent initialisation. backpropagate if needed to evaluate getter
						self.previousValue = self.currentValue	#			Make sure previousValue is available in case of dependent initialisation
						
					self.event = currentEvent ()				#		Certainly currentValue is up to date at this point
					self.propagate ()							#		Forward propagation
				finally:											# Even if getter raises an exception
					self.evaluating = False							#	Re-enable evaluation
				
		self.printTrace ('Evaluate, end', 'event')
		return self.currentValue						# Return possible updated currentValue
			
	def propagate (self):						# Forward propagation
		self.validate ()							#	Correct mistakes early, get report on changed node, rather than dependent one
		
		self.printTrace ('Writing to {0} links'.format (len (self.links)), 'event')
		for link in self.links:						#	For each GUI element associated with this node
			link.write ()							#		Update that GUI element
		
		for sinkNode in self.sinkNodes:				#	For all sinkNodes
			if not sinkNode.evaluating:				#		Unless sinkNode is already under evaluation
				sinkNode.evaluate ()				#			Make sure it evaluates, since no other node may ask it to
			else:
				sinkNode.printTrace ('Propagate, blocked', 'currentValue')					
									
	def act (self):						# Called at the end of transaction, to ensure updated values, e.g. on entering an event loop
		if hasattr (self, 'action'):	# "Old style" single action functionality kept for backward compatibility
			self.action ()
			
		for action in self.actions:		# Perform all "new style" chainable actions associated with this node
			action ()
			
	new = property (evaluate)													# Reading property yields value of node after current event

	old = property (lambda self: ifExpr (self.event == currentEvent (),			# Reading property yields value of node before current event
		self.previousValue,
		self.currentValue
	))
				
	touched = property (lambda self: self.event in (currentEvent (), 0) and self.event != 1)
	triggered = property (lambda self: self is triggerNode ())
	
	def convert (self, convertibleValue):
		return getAsTarget (convertibleValue, self.currentValue.__class__)
	
	def change (self, convertibleValue, retrigger = False):						# Initiate a change
		if app.handlingNotification:
			return																	#	Forms.Message.Show causes a redundant LostFocus message, that trigger an extra call to Node.change
	
		transactor.clear ()															#	Start new transaction early, to make it work for conversion errors as well
		self.previousValue = self.currentValue										#	Save previousValue early to enable rollback. No problem if currentValue remains unaltered.
		transactor.add (self)														#	Even if currentValue remains unaltered, the GUI should possibly be rolled back
		
		try:
			convertedValue = self.convert (convertibleValue)
			
			if retrigger or convertedValue != self.currentValue:					# If retrigger or value changed
				triggerNode.value = self											#	Remember that this node started the propagation
				self.invalidate ()													#	Invalidate this node and dependent nodes
				
				self.printTrace ('Change, before assignment', 'currentValue')
				self.currentValue = convertedValue									#	Store new, converted value in this node
				self.printTrace ('Change, after assignment', 'currentValue')
			
				self.event = currentEvent.getNext	()								#	Make this node valid
				
				self.propagate ()													#	Propagate new value to dependent nodes
				
				transactor.act ()													#	Late, since actions may need node values and may even enter event loops
			
		except Refusal as refusal:
			handleNotification (refusal)
			transactor.rollBack ()
			
		except Exception as exception:	# This is a barebones Python exception, so convert it to Eden exception
			handleNotification (Objection (exMessage (exception), report = exReport (exception)))
			transactor.rollBack ()
			
	def follow (self, convertibleValue, retrigger = False):
		if not transactor.contains (self):
			self.previousValue = self.currentValue
			transactor.add (self)
		
		convertedValue = self.convert (convertibleValue)
		
		if retrigger or convertedValue != self.currentValue:			
			self.invalidate ()
			self.printTrace ('Follow, before assignment', 'currentValue')
			self.currentValue = convertedValue									#	Store new, converted value in this node
			self.printTrace ('Follow, after assignment', 'currentValue')
			self.event = currentEvent ()										#	Make this node valid
			self.propagate ()													#	Propagate new value to dependent nodes
			
			# Don't call transactor.act here, since it would for the second time perform all actions
			# Since the new changed nodes are appended to the nodelist of the transaction, their actions are performed anyhow
						
	state = property (evaluate, lambda self, convertibleValue: self.follow (convertibleValue, True))
			
	def rollBack (self):						#	Restore previous state after exception in change of evaluate
		self.currentValue = self.previousValue		#	Restore previous value
		self.event = currentEvent ()				#	State is result of currentEvent, with a rollBack, even in case of a rollBack
		
		for link in self.links:						#	For each GUI element associated with this node
			link.write ()							#		Restore that GUI element
			
	def tagged (self, tag):
		self.tag = tag
		return self

class Link:	# Link between a node and a particular bareRead / bareWrite pair of the possible multiple bareRead / bareWrite pairs within a view
			# Maintains multiple reading / writing states per view so that e.g. caption can follow content
						
	def	__init__ (self, node, bareRead, bareWrite):					# Tie link to node and to bareRead / bareWrite pair
		node.links.append (self)										# Add this link to links of node
		
		self.bareRead = bareRead if bareRead else lambda params: None	# Remember bareRead
		self.reading = False											# Not busy reading
		
		self.bareWrite = bareWrite if bareWrite else lambda: None		# Remember bareWrite
		self.writing = False											# Not busy writing
		
		self.writeBack = True											# Allow this view to be written back to as result of reading it (auto formatting)
		
	def read (self, *params):				# Read info from this view into associated node
		if not self.writing:					# Prevent reading back half-written data, e.g. at re-checking items in a listView
			self.reading = True					#	Remember reading, to prevent writing while reading if no-writeback mode (see write method)
			self.bareRead (params)				#		Low level read from widget and / or event params
			self.reading = False				#	Remember not reading anymore
		
	def write (self):							# Write info from associated node to this view
		if self.writeBack or not self.reading:		# Prevent bareWrite as consequence of a read on the same view, if no-writeBack mode
			if not self.writing:					#	Prevent recursive bareWrite as side effect of node () call in bareWrite
				self.writing = True					#		Remember busy writing
				
				try:								#		If the widget is already instantiated
					self.bareWrite ()				#			Low level write to widget
				except AttributeError:				#		If widget is not yet instantiated (while passing parameters to execute)
					pass							#			Do nothing
				except TypeError:					#		If widget is not yet instantiated (while passing parameters to execute)
					pass							#			Do nothing
				except NameError, e:				#		!!! Tree drag&drop lifetime workaround
					print 'NameError in Link.write', str (e)
					
				self.writing = False				#		Remember not busy writing anymore
				
def getNode (valueOrNode, resultIfNone = None):
	if valueOrNode is None:	# e.g. valueOrNode == False should lead to condition == True
		return resultIfNone
	else:
		if valueOrNode.__class__ == Node:
			return valueOrNode
		else:	
			return Node (valueOrNode)

