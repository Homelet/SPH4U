import numpy as np
import matplotlib.pyplot as plt


class Point:
	def __init__(self, x, y):
		"""
		in centimeters
		"""
		self.x = x
		self.y = y
	
	
	@classmethod
	def c(cls, ls):
		return cls(ls[0], ls[1])


class Environment:
	def __init__(self, water_n, air_n):
		self.water_n = water_n
		self.air_n = air_n


def estimate(environment: Environment, eye: Point, fish: Point):
	pass


def detect(environment: Environment, eye: Point, fish_image: Point):
	"""
	the program takes in the coordinate of the human and the coordinate of the fish image, and try to resolve coordinate
	of the real fish
	Note : the distance between the eye and the mid point is approximately 4.19 cm
	:param eye: the location of the eye
	:param fish_image: the image of the fish
	:param environment: the environment variable
	:return: the real fish coordinate
	"""
	if eye.y < 0:
		raise RuntimeError("Eye should be above the water surface!")
	elif fish_image.y > 0:
		raise RuntimeError("Fish image should be under water surface!")
	# find the slope between the line and the fish
	a = find_slope(eye, fish_image)
	b = find_bias(a, fish_image)
	# find the x intercept of the line
	x_inter = (-b) / a
	# apply the equation and get the weight and bias of new line
	# arf = np.cos(np.arctan(a))
	arf = 1 / ((1 + a ** 2) ** 0.5)
	beta = arf * environment.air_n / environment.water_n
	# weight = np.tan(arccos(beta))
	weight = (1 - beta ** 2) ** 0.5 / beta
	# sign conversion
	weight = weight if a > 0 else -1 * weight
	bias = find_bias(weight, Point(x_inter, 0))
	# find the point
	y = weight * fish_image.x + bias
	return eye.x, eye.y, fish_image.x, fish_image.y, fish_image.x, y, x_inter, a, b, weight, bias


def find_slope(p1: Point, p2: Point):
	return (p1.y - p2.y) / (p1.x - p2.x)


def find_bias(slope, p: Point):
	return p.y - slope * p.x


def main(eye_loc, fish_img_loc, water_n=1.33, air_n=1):
	# perform the calculation eye_x=0, eye_y=12, fish_x=-50, fish_y=-30
	en = Environment(water_n=water_n, air_n=air_n)
	result = [detect(environment=en, eye=Point.c(test[0]), fish_image=Point.c(test[1])) for test in zip(eye_loc, fish_img_loc)]
	plot(result, water_n, air_n)
	plt.show()


def plot(result, water_n, air_n):
	"""
	result = [(0:eye_x, 1:eye_y, 2:fish_x, 3:fish_y, 4:fish_loc_x, 5:fish_loc_y, 6:x_inter, 7:a, 8:b, 9:weight, 10:bias), ...]
	"""
	# set the axes to the middle
	ax = plt.gca()
	ax.spines['right'].set_color('none')
	ax.spines['top'].set_color('none')
	ax.spines['bottom'].set_position(('data', 0))
	ax.spines['left'].set_position(('data', 0))
	ax.xaxis.set_ticks_position('bottom')
	ax.yaxis.set_ticks_position('left')
	
	# calculate the limit of each side
	x_max, x_min = max([max(pair[0], pair[2], pair[4], pair[6], 0) for pair in result]), min([min(pair[0], pair[2], pair[4], pair[6], 0) for pair in result])
	y_max, y_min = max([max(pair[1], pair[3], pair[5], 0) for pair in result]), min([min(pair[1], pair[3], pair[5], 0) for pair in result])
	plt.xlim(x_min - 20, x_max + 10)
	plt.ylim(y_min - 10, y_max + 10)
	
	# annotate key data
	# eye
	eyes = list(set([(pair[0], pair[1]) for pair in result]))
	for eye in eyes:
		plt.annotate("eye ({}, {})".format(eye[0], eye[1]), xy=(eye[0], eye[1]), xycoords="data", xytext=(20, 30), textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
		plt.scatter(eye[0], eye[1], 30, color="blue")
	
	# fish image
	fishes = list(set([(pair[2], pair[3]) for pair in result]))
	for fish in fishes:
		plt.annotate("fish image ({}, {})".format(fish[0], fish[1]), xy=(fish[0], fish[1]), xycoords="data", xytext=(-55, 20), textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"), color="green")
		plt.scatter(fish[0], fish[1], 30, color="green")
	
	# actual fish
	fishes_loc = list(set([(pair[4], pair[5]) for pair in result]))
	for fish in fishes_loc:
		plt.annotate("fish ({}, {})".format(fish[0], fish[1]), xy=(fish[0], fish[1]), xycoords="data", xytext=(-40, 10), textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
		plt.scatter(fish[0], fish[1], 30, color="blue")
	
	# refraction point
	refractions = list(set([pair[6] for pair in result]))
	for refraction in refractions:
		# plt.annotate("refraction point", xy=(refraction, 0), xycoords="data", xytext=(-100, 30), textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
		plt.scatter(refraction, 0, 30, color="red")
	
	# n values
	plt.annotate("n={}".format(air_n), xy=(x_min - 20, 1), xycoords="data", fontsize=12)
	plt.annotate("n={}".format(water_n), xy=(x_min - 20, y_min + 10), xycoords="data", fontsize=12)
	
	# plot the incident ray in - and it's continues ray in -- [fish_x, x_inter, a, b]
	incident_rays = list(set([(pair[0], pair[2], pair[6], pair[7], pair[8]) for pair in result]))
	for incident_ray in incident_rays:
		eye_x, fish_x, x_inter, a, b = incident_ray
		incident_ray_x = np.linspace(min(eye_x, x_inter), max(eye_x, x_inter), 256, endpoint=True)
		incident_ray_y = a * incident_ray_x + b
		
		incident_ray_x_continue = np.linspace(x_inter, fish_x, 256, endpoint=True)
		incident_ray_y_continue = a * incident_ray_x_continue + b
		
		plt.plot(incident_ray_x, incident_ray_y, color='blue', linewidth=1.0, linestyle="-")
		plt.plot(incident_ray_x_continue, incident_ray_y_continue, color='green', linewidth=1.0, linestyle="--")
	
	# plot the normal
	normals = list(set([pair[6] for pair in result]))
	for x_inter in normals:
		normal_x = np.full((256,), x_inter)
		normal_y = np.linspace(y_min, y_max, 256, endpoint=True)
		
		plt.plot(normal_x, normal_y, color='red', linewidth=1.0, linestyle="--")
	
	# plot the predicted fish ray_1 [x_inter, weight , bias]
	ray_1s = list(set([(pair[6], pair[9], pair[10]) for pair in result]))
	for ray_1 in ray_1s:
		x_inter, weight, bias = ray_1
		refraction_ray_x = np.linspace(x_inter, x_min if weight > 0 else x_max, 256, endpoint=True)
		refraction_ray_y = weight * refraction_ray_x + bias
		
		plt.plot(refraction_ray_x, refraction_ray_y, color='blue', linewidth=1.0, linestyle="-")
	
	# plot the predicted fish ray_2 (the one goes up)
	ray_2s = list(set([pair[2] for pair in result]))
	for fish_x in ray_2s:
		fish_ray_2_x = np.full((256,), fish_x)
		fish_ray_2_y = np.linspace(y_min - 5, y_max + 5, 256, endpoint=True)
		
		plt.plot(fish_ray_2_x, fish_ray_2_y, color='blue', linewidth=1.0, linestyle="--")


if __name__ == '__main__':
	main([[0, 20], [0, 10]],
	     [[-50, -30]])
