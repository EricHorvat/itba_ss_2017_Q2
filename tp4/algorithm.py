
class Algorithm(object):
	
	def __init__(self, r, v, a_function):
		self.a_function = a_function
		self.r = r
		self.v = v
		self.a = a_function(r = r, v = v)
		self.r_history = []#[r]
		self.v_history = []#[v]
		self.a_history = []#[self.a]

	def loop(self, *params):
		self.basic_loop(params) if len(params) > 0 else self.basic_loop()
		self.r_history.append(self.r)
		self.v_history.append(self.v)
		self.a_history.append(self.a)

	def basic_loop(self):
		raise "Not implemented method"



		
