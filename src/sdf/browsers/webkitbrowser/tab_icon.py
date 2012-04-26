# *- encoding: utf-8 -*
'''
Created on 12/08/2010

@author: iavas
'''
from PyQt4.QtGui import QIcon, QPixmap


class TabIcon(QIcon):
	"Un ícono de tab"

	def __init__(self):
		QIcon.__init__(self)
		self.addPixmap(
					QPixmap(":/icons/text-html.png"),
					QIcon.Normal,
					QIcon.Off
					)
