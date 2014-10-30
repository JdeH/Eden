# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

from eden.edenLib.base import *
from eden.edenLib.xml import *

try:
	from config import *
except:
	try:
		def expand (entry):
			if len (entry) > 3 and entry [0] == '(':
				parts = entry [1:] .split (')', 1)
				return getattr (application, parts [0]) + parts [1]
			else:
				return entry
	
		xmlDict = readXmlDict ('config.xml')
		
		for key in xmlDict:
			entry = [expand (item) for item in xmlDict [key]]
			
			if len (entry):
				if len (entry) > 1:
					setattr (application, key, entry)
				else:
					setattr (application, key, entry [0])
	except:
		pass

from eden.edenLib.platform import *
from eden.edenLib.store import *
from eden.edenLib.node import *	
from eden.edenLib.view import *
from eden.edenLib.panel import *
from eden.edenLib.module import *

from eden.edenExtra.tweakers import *


