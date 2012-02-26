import threading


class SupermodelDebugInfo(threading.local):

	def __getattr__(self, name):
		if name == 'stack':
			self.stack = [None]
			return self.stack
		return super(SupermodelDebugInfo, self).__getattr__(name)

debuginfo = SupermodelDebugInfo()
