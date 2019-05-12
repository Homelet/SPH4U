import numpy as np
import matplotlib.pyplot as plt


class Point:
	def __init__(self, x, y):
		"""
		in centimeters
		"""
		self.x = x
		self.y = y


class Environment:
	def __init__(self, water_n, air_n):
		self.water_n = water_n
		self.air_n = air_n


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
	# find the slope between the line and the fish
	a = find_slope(eye, fish_image)
	b = find_bias(a, fish_image)
	# find the x intercept of the line
	x_inter = (-b) / a
	# apply the equation and get the weight and bias of new line
	arf = np.arctan(a)
	weight = 1 / np.arcsin((np.cos(arf) * environment.air_n / environment.water_n))
	bias = find_bias(weight, Point(x_inter, 0))
	# find the point
	y = weight * fish_image.x + bias
	return a, b, x_inter, weight, bias, Point(fish_image.x, y)


def find_slope(p1: Point, p2: Point):
	return (p1.y - p2.y) / (p1.x - p2.x)


def find_bias(slope, p: Point):
	return p.y - slope * p.x


def main(water_n=1.33, air_n=1, eye_x=0, eye_y=12, fish_x=-50, fish_y=-30):
	# perform the calculation
	a, b, x_inter, weight, bias, fish_loc = detect(environment=Environment(water_n=water_n, air_n=air_n), eye=Point(x=eye_x, y=eye_y), fish_image=Point(x=fish_x, y=fish_y))
	
	# set the axes to the middle
	ax = plt.gca()
	ax.spines['right'].set_color('none')
	ax.spines['top'].set_color('none')
	ax.spines['bottom'].set_position(('data', 0))
	ax.spines['left'].set_position(('data', 0))
	ax.xaxis.set_ticks_position('bottom')
	ax.yaxis.set_ticks_position('left')
	
	# calculate the limit of each side
	x_max, x_min, y_max, y_min = max(eye_x, fish_x, fish_loc.x) + 10, min(eye_x, fish_x, fish_loc.x) - 20, max(eye_y, fish_y, fish_loc.y) + 10, min(eye_y, fish_y, fish_loc.y) - 10
	plt.xlim(x_min, x_max)
	plt.ylim(y_min, y_max)
	
	# annotate key data
	# eye
	plt.annotate("eye ({}, {})".format(eye_x, eye_y), xy=(eye_x, eye_y), xycoords="data", xytext=(20, 30), textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
	plt.scatter(eye_x, eye_y, 30, color="blue")
	
	# fish image
	plt.annotate("fish image ({}, {})".format(fish_x, fish_y), xy=(fish_x, fish_y), xycoords="data", xytext=(-55, 20), textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
	plt.scatter(fish_x, fish_y, 30, color="blue")
	
	# actual fish
	plt.annotate("fish ({}, {})".format(fish_loc.x, fish_loc.y), xy=(fish_loc.x, fish_loc.y), xycoords="data", xytext=(-40, 20), textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
	plt.scatter(fish_loc.x, fish_loc.y, 30, color="blue")
	
	# refraction point
	plt.annotate("refraction point", xy=(x_inter, 0), xycoords="data", xytext=(-100, 30), textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
	plt.scatter(x_inter, 0, 30, color="red")
	
	# n values
	plt.annotate("n={}".format(air_n), xy=(x_min, 1), xycoords="data", fontsize=12)
	plt.annotate("n={}".format(water_n), xy=(x_min, y_min + 10), xycoords="data", fontsize=12)
	
	# plot the incident ray in - and it's continues ray in --
	incident_ray_x = np.linspace(0, x_inter, 256, endpoint=True)
	incident_ray_y = a * incident_ray_x + b
	
	incident_ray_x_continue = np.linspace(x_inter, fish_x, 256, endpoint=True)
	incident_ray_y_continue = a * incident_ray_x_continue + b
	
	plt.plot(incident_ray_x, incident_ray_y, color='blue', linewidth=1.0, linestyle="-")
	plt.plot(incident_ray_x_continue, incident_ray_y_continue, color='blue', linewidth=1.0, linestyle="--")
	
	# plot the normal
	normal_x = np.full((256,), x_inter)
	normal_y = np.linspace(y_min, y_max, 256, endpoint=True)
	
	plt.plot(normal_x, normal_y, color='red', linewidth=1.0, linestyle="--")
	
	# plot the predicted fish ray_1
	refraction_ray_x = np.linspace(x_inter, x_min, 256, endpoint=True)
	refraction_ray_y = weight * refraction_ray_x + bias
	
	plt.plot(refraction_ray_x, refraction_ray_y, color='blue', linewidth=1.0, linestyle="-")
	
	# plot the predicted fish ray_2 (the one goes up)
	fish_ray_2_x = np.full((256,), fish_x)
	fish_ray_2_y = np.linspace(y_min + 5, y_max - 5, 256, endpoint=True)
	
	plt.plot(fish_ray_2_x, fish_ray_2_y, color='red', linewidth=1.0, linestyle="--")
	
	plt.show()


if __name__ == '__main__':
	main()
