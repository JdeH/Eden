# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

from .edenLib.base import *
from .edenLib.util import *
from .edenLib.xml import *

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

from .edenLib.platform import *
from .edenLib.store import *
from .edenLib.node import *	
from .edenLib.view import *
from .edenLib.panel import *
from .edenLib.module import *

from .edenExtra.tweakers import *


