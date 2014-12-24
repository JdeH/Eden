Name
====

Eden - Event Driven Evaluation Nodes.


Licence
=======

QQuick licence, see www.qquick.org.


Purpose
=======

Eden is a library that allows rapid declarative construction of applications.


Installation
============


Put the eden (lowercase!) subdirectory of Eden into the site-packages or the dist-packages directory of the Python version you wish to use.
If you want to install it under multiple Python versions, e.g. IronPython 2.7 and CPython 2.7, you can use a symlink (so NOT a shortcut, google for 'mklink').

N.B.
The WinForms (stable) version works with IronPython 2.7.
The Kyvi version (under development) works with CPython 2.7 and Kivy 1.8 you can e.g. use the Python 2.7 that comes with Portable Kivy for Windows.
The Kyvi version should also run under Linux, although that is only tested infrequently.


Recent changes
==============

Kivy version:
	Dropdown menus added
	Modal views (dialogs) added

WinForms version:
	None
	
	
How does it work
================

All program logic and processing is specified by functional dependencies between Nodes.
Dependencies can be cyclic and exception handling by rollback is provided.
Nodes can be used in any situation, for console apps, batch apps, or apps using any GUI library that has a Python API.

To make life easier, a set of Views is available.
Each View is a thin layer on top of a GUI Widget class from the underlying GUI library.
Views can be connected to Nodes using Links.
Typically a View will be connected to multiple Nodes, but also a Node can be connected to multiple Views.
In this way a complete GUI app can be "wired" together.
Layout is dynamic.
Both data and layout are persistent.


Practical experiences using Eden
================================

Using Eden in everyday practice has proven a pleasure.
Eden has been in use for multiple years now by multiple people working on diverse engineering projects.
The resulting applications involve dozens of modules, most of them with dozens of nodes, some nodes carrying many megabytes of data.
A characteristic of both projects is that requirements rapidly evolved during the project.
With Eden it proved remarkably easy to follow the changing requirements.
In spite of the fact that requirements changed frequently and deeply, application structure has remained lean and clean.
Unfortunately these projects, that otherwise might have very well served as coding and style examples, were all proprietary.
One of the people working on a project remarked that with Eden, coding clean, flexible and maintainable program logic was as easy and routinely as drawing up a shopping list.


Learning Eden
=============

Although the tutorial examples are simple for anyone to comprehend, they by far don't cover all the features.
Moreover they are too small to reveal issues of overall program organisation, like the use of the Module mechanism.
Using Eden in an effective way for a non-trivial app has a steep (but short) learing curve.
It has proven feasible to get a "fresh" developer upto speed in a few days of side by side tutoring. There's a real need for a freely available elaborated example, though.
Currently I concentrate upon the CPython + Kivy version, since mobile- and tablet platforms are where most of the action is. One public domain application that uses the IronPython + WinForms version is Wave (see www.qquick.org).
It is, however, not yet complete and to specialistic to serve as an example.
A killer app would help. As soon as the CPython + Kivy version has some body, I hope to come up with a free multiplatform app that proves the point as well as is suitable as an elaborated example.


Status
======

Eden for IronPython + WinForms has been used for production programming for multiple years now by several people.
Eden for CPython + Kivy is in the early stages of development.


Known bugs
==========

External drag and drop format incompatible with external cut and paste format.


Getting started
===============


Using IronPython + WinForms
-----------------------------

Tutorial programs are in the tutorialWinForms directory


Using CPython + Kivy
----------------------

Some preliminary examples are in the preliminaryTutorialKivy directory


Compatibility
=============

The IronPython + WinForms version has been tested and used extensively on Windows from XP to 8.1.
It has never been tested on Linux + Mono.

The Views of the CPython + Kivy version will reflect the particularities of Kivy and of the diversity of platforms it should run at.
So, although there will be many common elements, there will be no one to one correspondence between Views based on Kivy and Views based on WinForms.

The essence of the matter, the API of the underlying Event Driven Evaluation Nodes pattern, however, is the same. Only the GUI part differs.


Future
======

Plans are to build out and fully document Eden and stay committed to it for a long time to come.
However not any, even implied guarantee is made with respect to its continuity.
Time will have to prove whether it acquires mindshare.

There exists a proprietary commercial port of Eden to Qt using PyQt.
It runs on Linux and Windows and was made and is owned by a third party.
It is not available as open source software, but its existence has proven the portability of Eden.

Some work has been done on a TkInter version, but it has been abandoned in favor of Kivy.


Co-Development
==============

The code of the Eden project is hosted by GitHub.
The plan is to involve more developers as soon as the Kivy version is well underway.
Completing the TkInter version e.g. would be great...
Coding for Eden requires thorough understanding of the Node/Link/View concepts, including rollback and cyclic dependencies.
The essence is in the Node library module.
Although it is a small, extensively commented module, it is quite hard grab the nifty details.
A very concise description is what I'll have to come up with...


Enjoy!
======

Jacques de Hooge
jacques.de.hooge@qquick.org
