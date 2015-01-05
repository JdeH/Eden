# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

from ..edenLib.base import *
from ..edenLib.util import *

if 'WinForms' in application.platform:
	from .winForms.tweakers import *
	
elif 'Kivy' in application.platform:
	from .kivy.tweakers import *
