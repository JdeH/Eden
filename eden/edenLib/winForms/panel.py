# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

from ..node import *
from ..store import *
from ..view import *

# import sys

# sys.LoadAssemblyByName("System.Drawing")
# sys.LoadAssemblyByName("System.Windows.Forms")

import clr

clr.AddReference ('System.Drawing')
clr.AddReference ('System.Windows.Forms')

from System import Drawing
from System.Windows import Forms

class HtmlView:
	def __init__ (self, urlNode, backNode = None, forwardNode = None, backEnabledNode = None, forwardEnabledNode = None, tweaker = None):
		self.urlNode = urlNode
		self.backNode = backNode
		self.forwardNode = forwardNode
		self.backEnabledNode = backEnabledNode
		self.forwardEnabledNode = forwardEnabledNode
		
		self.stretchHeight = True
	
	def createWidget (self):
		self.widget = Forms.WebBrowser ()
		self.widget.AutoSize = True
		self.widget.Dock = Forms.DockStyle.Fill
		
		def bareReadUrl (params):
			self.urlNode.change (self.widget.Url.ToString ())
		
		def bareWriteUrl ():
			self.widget.Url = System.Uri (self.urlNode.new)
		
		self.urlLink = Link (self.urlNode, bareReadUrl, bareWriteUrl)
		self.widget.Navigated += self.urlLink.read

		self.urlLink.write ()
		
		if not self.backNode is None:
			self.backLink = Link (self.backNode, None, self.widget.GoBack)
			
		if not self.forwardNode is None:
			self.forwardLink = Link (self.forwardNode, None, self.widget.GoForward)

		if not self.backEnabledNode is None:
			def bareReadBackEnabled (params):
				self.backEnabledNode.follow (self.widget.CanGoBack)

			self.backEnabledLink = Link (self.backEnabledNode, bareReadBackEnabled, None)
			self.widget.CanGoBackChanged += self.backEnabledLink.read

		if not self.forwardEnabledNode is None:
			def bareReadForwardEnabled (params):
				self.forwardEnabledNode.follow (self.widget.CanGoForward)

			self.forwardEnabledLink = Link (self.forwardEnabledNode, bareReadForwardEnabled, None)
			self.widget.CanGoForwardChanged += self.forwardEnabledLink.read

		return self.widget

class SelectFileView:
	@classmethod
	def show (cls, fileNameListNode, caption, filterOptions, multiSelect = False, tweaker = None):
		widget = cls.getSelectWidget (multiSelect)
		widget.SupportMultiDottedExtensions = True
		widget.Title = caption
		widget.Filter = '|'.join ([filterOption [0] + '|*' +  ';*'.join (filterOption [1]) for filterOption in filterOptions])
		if len (fileNameListNode.new):
			widget.FileName = fileNameListNode.new [0] .replace ('/', '\\')
		else:
			widget.FileName = ''

		if tweaker:
			tweaker (widget)	

		if widget.ShowDialog () == Forms.DialogResult.OK:
			fileNameListNode.change ([fileName.replace ('\\', '/') for fileName in widget.FileNames], True)

class OpenFileView (SelectFileView):
	@classmethod
	def getSelectWidget (cls, multiSelect):
		widget = Forms.OpenFileDialog ()
		widget.Multiselect = multiSelect
		return widget

class SaveFileView (SelectFileView):
	@classmethod
	def getSelectWidget (cls, multiSelect):
		widget = Forms.SaveFileDialog ()
		widget.OverwritePrompt = False
		return widget
			
class SelectPathView:
	@classmethod
	def show (cls, pathNode, caption, tweaker = None):
		widget = Forms.FolderBrowserDialog ()
		widget.Description = caption
		widget.SelectedPath = pathNode.new.replace ('/', '\\')

		if tweaker:
			tweaker (widget)	

		if widget.ShowDialog () == Forms.DialogResult.OK:
			pathNode.change (widget.SelectedPath.replace ('\\', '/'), True)
			
class ButtonId:
	Abort, Cancel, Ignore, No, Null, Ok, Retry, Yes = range (8)

class MessageView:
	Results = {
		Forms.DialogResult.Abort : ButtonId.Abort,
		Forms.DialogResult.Cancel : ButtonId.Cancel,
		Forms.DialogResult.Ignore : ButtonId.Ignore,
		Forms.DialogResult.No : ButtonId.No,
		Forms.DialogResult.None : ButtonId.Null,
		Forms.DialogResult.OK : ButtonId.Ok,
		Forms.DialogResult.Retry : ButtonId.Retry,
		Forms.DialogResult.Yes : ButtonId.Yes
	}
	
	FormsButtonCombinations = {
		frozenset ([ButtonId.Abort, ButtonId.Retry, ButtonId.Ignore]) : Forms.MessageBoxButtons.AbortRetryIgnore,
		frozenset ([ButtonId.Ok]) : Forms.MessageBoxButtons.OK,
		frozenset ([ButtonId.Ok, ButtonId.Cancel]) : Forms.MessageBoxButtons.OKCancel,
		frozenset ([ButtonId.Retry, ButtonId.Cancel]) : Forms.MessageBoxButtons.RetryCancel,
		frozenset ([ButtonId.Yes, ButtonId.No]) : Forms.MessageBoxButtons.YesNo,
		frozenset ([ButtonId.Yes, ButtonId.No, ButtonId.Cancel]) : Forms.MessageBoxButtons.YesNoCancel
	}
		
	FormsIcons = {
		'asterisk' : Forms.MessageBoxIcon.Asterisk,
		'error' : Forms.MessageBoxIcon.Error,
		'exclamation' : Forms.MessageBoxIcon.Exclamation,
		'hand' : Forms.MessageBoxIcon.Hand,
		'information' : Forms.MessageBoxIcon.Information,
		'none' : Forms.MessageBoxIcon.None,
		'question' : Forms.MessageBoxIcon.Question,
		'stop' : Forms.MessageBoxIcon.Stop,
		'warning' : Forms.MessageBoxIcon.Warning
	}
	
	@classmethod
	def show (cls, buttonIds, message, caption, icon = 'none'):
		try:
			formsButtonCombination = cls.FormsButtonCombinations [frozenset (buttonIds)]
		except:
			print 'Internal error: Invalid combination of buttons ' + str (buttonIds) + ' in call to showMessageView'
			
		try:
			formsIcon = cls.FormsIcons [icon]
		except:
			print 'Internal error: Invalid icon \'' + icon + '\' in call to showMessageView'
							
		return cls.Results [Forms.MessageBox.Show (message, caption, formsButtonCombination, formsIcon)]
		
class NotificationView (MessageView):
	@classmethod
	def show (cls, notification):
		return MessageView.show ([ButtonId.Ok], notification.message, notification.caption, notification.icon)

app.notificationShower = NotificationView.show
