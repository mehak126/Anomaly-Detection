import socket
import sys
import math
from copy import deepcopy
import threading
import random
# import subprocess
import time

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class send_data:
	data = "" 
	flag = 0
	def __init__(self,d,f):
		self.data = d
		self.flag = f



class Coordinate : #Class which stores x,y,z coordinate and the cluster of each point on the clustering graph
	x = 0.0
	y = 0.0
	z = 0.0
	c = 0


	def __init__(self, i, j, k, cluster): #constructor
		self.x = i
		self.y = j
		self.z = k
		self.c = cluster

#arrays for storing initial cluster points of server 1, 2 and 3 respectively 
characteristic_points_s1 = []
characteristic_points_s2 = []
characteristic_points_s3 = []

counter = [0,0,0,0] #counter for TP,FP,TN,FN

n = 1000 #initial cluster points for each server
t=5 #no. of threads
k = 3 #no. of clusters

data=[[Coordinate(0,0,0,0) for i in range(n)] for j in range(3)] #array to store coordinates of data points for each server (including initial and new points)
means = [[Coordinate(0,0,0,0) for i in range(k)] for j in range(3)] #array to store coordinates of means of clusters for each server
max_dist = [[0 for i in range(k)] for j in range(3)] #array to store data point at maximum distance from the cluster center for each server
clusterCardinality = [[1 for i in range(n)] for j in range(3)] #array to store cardinality of each cluster for each server

global lock
global change 
change = True
terminate=0

global anomalous_count
anomalous_count = 0


def main(server_id): #function which sets up a TCP connection with the server specified by the argument server_id and receives data from it
	
	#setting the server IP and Port for the TCP connection according to the id
	if server_id == 0:
		serverName = '127.0.0.1'
		serverPort = 12345

	elif server_id == 1:
		serverName = '127.0.0.1'
		serverPort = 12346

	else:
		serverName = '127.0.0.1'
		serverPort = 12348


	#Receiving text data from the server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((serverName,serverPort))
	ftp_sentence = 'Send ftp data'
	s.send(ftp_sentence)	
	ftp_data = s.recv(1024)
	temp = s.recv(1024)	
	while(temp != ''):
		temp = s.recv(1024)
		ftp_data += temp
	flag = ftp_data[0]	
	if flag == 1:
		anomalous_count += 1
	ftp_size = sys.getsizeof(ftp_data[1:])
	s.close()
	

	#Receiving image (jpg) data from the server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((serverName,serverPort))
	jpg_sentence = 'Send jpg data'
	s.send(jpg_sentence)	
	jpg_data = s.recv(1024)
	temp = s.recv(1024)	
	while(temp != ''):
		temp = s.recv(1024)
		jpg_data += temp
	jpg_size = sys.getsizeof(jpg_data[1:])
	s.close()

	#Receiving video data from the server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((serverName,serverPort))	
	vid_sentence = 'Send video data'
	s.send(vid_sentence)	
	vid_data = s.recv(1024)
	temp = s.recv(1024)	
	while(temp != ''):
		temp = s.recv(1024)
		vid_data += temp
	vid_size = sys.getsizeof(vid_data[1:])
	s.close()

	#calculating ratios of received data
	ratio = [0.0] * 3 #0-> text, 1-> jpg, 2-> vid 
	ratio[0] = ftp_size
	ratio[1] = jpg_size
	ratio[2] = vid_size

	mini = min(min(ratio[0],ratio[1]),ratio[2])
	for i in range(3):
		ratio[i] = float(ratio[i]) / mini

	#appending the ratio as a data point to the cluster points of the appropriate server
	if server_id == 0:
		characteristic_points_s1.append(Coordinate(ratio[0], ratio[1], ratio[2], k))
	elif server_id == 1:
		characteristic_points_s2.append(Coordinate(ratio[0], ratio[1], ratio[2], k))
	else:
		characteristic_points_s3.append(Coordinate(ratio[0], ratio[1], ratio[2], k))

	return (flag,Coordinate(ratio[0],ratio[1],ratio[2],k))


def calc_distance(point1, point2): #Function which calculates and returns the euclidean distance between two coordinates
	return math.sqrt(math.pow((point1.x-point2.x),2) + math.pow((point1.y-point2.y),2) + math.pow((point1.z - point2.z),2))


def initialize(server): #function for calculating initial cluster centers using kmeans++
	totaldist = 0					#Will be used to calculate mean
	newcentre = random.randint(0,n-1)
	count=0						#To keep count of the means initialized
	templist=deepcopy(data[server])			#The zeroth mean is taken up at random 
	means[server][count]=templist[newcentre]
	count+=1

	while count < k :

		totaldist=0
		temp = []
		dist = []
		
		'''The process of initialization works by appending the means one at a time and clustering the points according
		to squared Euclidean distance. So this loop runs for all n points, 'count' means at a time.
		'''
		for i in range(n):
			minimum = float('inf')
			for j in range(count):
				if calc_distance(data[server][i],means[server][j]) < minimum :
					newcentre = j

			#print("server = " + str(server) + " i = " + str(i) + " newcentre = " + str(newcentre))
			dist.append(math.pow(calc_distance(data[server][i],means[server][newcentre]),2))
			totaldist += dist[i]
		''' The next loop is creating an array for the points in which the difference between ith and (i-1)th position tells
		us the probability of picking that point, according to definition of kmeans++
		'''
		for i in range(n):
			if i == 0 :
				temp.append(dist[i]/totaldist)
			else :
				temp.append(temp[i-1] + dist[i]/totaldist)

		point = random.uniform(0,1)
		for i in range(n):
			if (point <= temp[i]):
				#means.append(data[i])
				fl = True
				for j in range(count):
					if(means[server][j].x == templist[i].x and means[server][j].y == templist[i].y and means[server][j].z == templist[i].z):
						fl = False
						break
				if fl == False:
					continue
				means[server][count]=templist[i]
				count += 1
				break


def updateMeans(server): #Calculating cluster means for the server specified by 'server'
	templ=deepcopy(data[server])
	for i in range(k):
		means[server][i].x = 0
		means[server][i].y = 0
		means[server][i].z = 0
		max_dist[server][i] = 0
		clusterCardinality[server][i]=0

	for i in range(len(templ)):
		means[server][data[server][i].c].x += templ[i].x
		means[server][data[server][i].c].y += templ[i].y
		means[server][data[server][i].c].z += templ[i].z
		clusterCardinality[server][data[server][i].c] += 1

	for i in range(k):
		if(clusterCardinality[server][i]!=0):
			means[server][i].x /= clusterCardinality[server][i]
			means[server][i].y /= clusterCardinality[server][i]
			means[server][i].z /= clusterCardinality[server][i]

	for i in range(len(templ)):
		if(calc_distance(data[server][i],means[server][data[server][i].c]) > max_dist[server][data[server][i].c]):
			max_dist[server][data[server][i].c] = calc_distance(data[server][i], means[server][data[server][i].c])	


def cluster(ID,server): #Calculating cluster of the data points assigned to thread with ID "ID" for the server "server"
	global change
	global lock
	start=ID * (n/t)
	if ID==(t-1):
		end=n
	else:
		end=start + (n/t)
	for i in range(start,end):
		min = float('inf')
		for j in range(k):
			temp = calc_distance(data[server][i],means[server][j])
			if temp < min :
				min = temp
				newCluster = j
		lock.acquire()
		try:
			if newCluster!=data[server][i].c:
				change = True
				data[server][i].c = newCluster
		finally:
			lock.release()
	return

def get_cluster(point,server,flag): #Function to get cluster of the new data point and flag it as normal or anomalous

	ret_type = 0
	min_dist = float('inf')
	anomalous = True

	for i in range(len(means[server])):
		if calc_distance(point, means[server][i]) <= (max_dist[server][i]*1.05) : #checking if the point lies within 10% of the farthest point from the cluster center
			anomalous = False
			if(calc_distance(point, means[server][i]) < min_dist):
				point.c = i;
				min_dist = calc_distance(point, means[server][i])


	if anomalous == True :
		print("\nAnomalous data detected in server " + str(server) + "\n")
		if flag == "0":
			#print("FALSE ANOMALY!!!!")
			counter[3]+=1
			ret_type = 3
		else:
			counter[2]+=1
			ret_type = 2

		#turning on the appropriate leds of the raspberry pi according to the server
		# if server == 0:
		# 	subprocess.call('echo 1 | sudo tee /sys/class/leds/led1/brightness', shell = True)
		# elif server == 1:
		# 	subprocess.call('echo 1 | sudo tee /sys/class/leds/led0/brightness', shell = True)
		# else:
		# 	subprocess.call('echo 1 | sudo tee /sys/class/leds/led0/brightness', shell = True)
		# 	subprocess.call('echo 1 | sudo tee /sys/class/leds/led1/brightness', shell = True)
		# time.sleep(2)



	else : #updating cluster center with the new point included
		# subprocess.call('echo 0 | sudo tee /sys/class/leds/led0/brightness', shell = True)
		# subprocess.call('echo 0 | sudo tee /sys/class/leds/led1/brightness', shell = True)
		if flag == "1":
		#	print("FALSE NORMAL!!!")
			counter[1]+=1
			ret_type = 1
		else:
			counter[0]+=1
			ret_type = 0
		data[server].append(point)
		updateMeans(server)
	return ret_type
			

def printClusterMeans(server): #Function to print coordinates of means of clusters for the server specified by 'server'
	print("Server " + str(server))
	for i in range(len(means[server])):
		print(str(means[server][i].x) + ", " + str(means[server][i].y) + ", " + str(means[server][i].z)  +" dist  "+ str(max_dist[server][i]) + " cardinality: " + str(clusterCardinality[server][i]))


def kmeans(pointArray, server): #performing clustering of the points in the array 'pointArray' correspoinding to the server 'server'
	global change
	change = True
	temp_list = deepcopy(pointArray)
	for i in range(n):
		data[server][i] = temp_list[i]

	#clusterCardinality = [1] * len(characteristic_points_s1)
	
	temp_points=deepcopy(data[server])		#Initializing to avoid errors
	for i in range(k):
		means[server][i] = temp_points[i]

	initialize(server)

	global lock
	lock=threading.Lock()
	terminate = 0
	while change:
		change = False
		terminate += 1
		if terminate==10:	#Max number of reclustering set to 10
			break
		allThreads=[]
		for i in range(t):
			allThreads.append(threading.Thread(target=cluster, args=(i,server,))) 
			allThreads[i].start()

		for s in range(t):
			allThreads[s].join()
		updateMeans(server)	


if __name__ == '__main__':

		#turning off both leds of the raspberry pi
		# subprocess.call('echo 0 | sudo tee /sys/class/leds/led0/brightness', shell = True)
		# subprocess.call('echo 0 | sudo tee /sys/class/leds/led1/brightness', shell = True)

		#getting 'n' points for initial clustering from the 3 servers
		for i in range(0,3):
			for j in range(n):
				point = main(i)

		#Forming clusters of the initial points of each server
		kmeans(characteristic_points_s1,0);
		kmeans(characteristic_points_s2,1);
		kmeans(characteristic_points_s3,2);

		plt.ion()
		

		fig = plt.figure(1)
		ax1 = fig.add_subplot(111, projection='3d')
		xs = [val.x for val in characteristic_points_s1]
		xs = list(map(float,xs))
		xs = np.array(xs)

		
		ys = [val.y for val in characteristic_points_s1]
		ys = list(map(float,ys))
		ys = np.array(ys)

		zs = [val.z for val in characteristic_points_s1]
		zs = list(map(float,zs))
		zs = np.array(zs)

		for i in range(len(xs)):
			#print(characteristic_points_s1[i].c)
			if data[0][i].c == 0:
				ax1.scatter(data[0][i].x, data[0][i].y, data[0][i].z, c='y', marker = 'o',zorder = 10)
			elif data[0][i].c == 1:
				ax1.scatter(data[0][i].x, data[0][i].y, data[0][i].z, c='grey', marker = 'o',zorder = 10)
			else:
				ax1.scatter(data[0][i].x, data[0][i].y, data[0][i].z, c='pink', marker = 'o',zorder = 10)


		plt.draw()
		#plt.hold(True)
		plt.pause(2)
		# plt.clf()
	#	plt.show()
		# 	plt.draw()
		# 	plt.pause(0.2)
		# plt.clf


		# X = np.linspace( ,  2 * np.max(theta_0) - np.min(theta_0)  , num = 200)
		# Y = np.linspace( np.min(theta_1) -1 ,  np.max(theta_1) +1  , num = 200)



		# fig = plt.figure()
		# ax = fig.add_subplot(111, projection='3d')
		# xs = [val.x for val in characteristic_points_s2]
		# xs = list(map(float,xs))
		# xs = np.array(xs)

		
		# ys = [val.y for val in characteristic_points_s2]
		# ys = list(map(float,ys))
		# ys = np.array(ys)

		# zs = [val.z for val in characteristic_points_s2]
		# zs = list(map(float,zs))
		# zs = np.array(zs)

		# #for i in range(len(xs)):
		# ax.scatter(xs, ys, zs, c='r', marker = 'o')
		# plt.show()
		# plt.pause(0.2)
		# plt.clf()
		# plt.close()


		# fig = plt.figure()
		# ax = fig.add_subplot(111, projection='3d')
		# xs = [val.x for val in characteristic_points_s3]
		# xs = list(map(float,xs))
		# xs = np.array(xs)

		
		# ys = [val.y for val in characteristic_points_s3]
		# ys = list(map(float,ys))
		# ys = np.array(ys)

		# zs = [val.z for val in characteristic_points_s3]
		# zs = list(map(float,zs))
		# zs = np.array(zs)

		# #for i in range(len(xs)):
		# ax.scatter(xs, ys, zs, c='g', marker = 'o')
		# plt.show()
		# plt.close()



		fig = plt.figure(2)
		ax2 = fig.add_subplot(111, projection='3d')
		xs = [val.x for val in characteristic_points_s2]
		xs = list(map(float,xs))
		xs = np.array(xs)

		
		ys = [val.y for val in characteristic_points_s2]
		ys = list(map(float,ys))
		ys = np.array(ys)

		zs = [val.z for val in characteristic_points_s2]
		zs = list(map(float,zs))
		zs = np.array(zs)

		for i in range(len(xs)):
			#print(characteristic_points_s1[i].c)
			if data[1][i].c == 0:
				ax2.scatter(data[1][i].x, data[1][i].y, data[1][i].z, c='y', marker = 'o',zorder = 10)
			elif data[1][i].c == 1:
				ax2.scatter(data[1][i].x, data[1][i].y, data[1][i].z, c='grey', marker = 'o',zorder = 10)
			else:
				ax2.scatter(data[1][i].x, data[1][i].y, data[1][i].z, c='pink', marker = 'o',zorder = 10)

		plt.draw()
		#plt.hold(True)
		plt.pause(2)
		# plt
	#	plt.clf()
		

	#	plt.show()








		fig = plt.figure(3)
		ax3 = fig.add_subplot(111, projection='3d')
		xs = [val.x for val in characteristic_points_s3]
		xs = list(map(float,xs))
		xs = np.array(xs)

		
		ys = [val.y for val in characteristic_points_s3]
		ys = list(map(float,ys))
		ys = np.array(ys)

		zs = [val.z for val in characteristic_points_s3]
		zs = list(map(float,zs))
		zs = np.array(zs)

		for i in range(len(xs)):
			#print(characteristic_points_s1[i].c)
			if data[2][i].c == 0:
				ax3.scatter(data[2][i].x, data[2][i].y, data[2][i].z, c='y', marker = 'o',zorder = 10)
			elif data[2][i].c == 1:
				ax3.scatter(data[2][i].x, data[2][i].y, data[2][i].z, c='grey', marker = 'o',zorder = 10)
			else:
				ax3.scatter(data[2][i].x, data[2][i].y, data[2][i].z, c='pink', marker = 'o',zorder = 10)
		
		plt.draw()
		#plt.hold(True)
		plt.pause(2)
		# plt.clf()
	#	plt.close()

		#labels
		x = [data[0][0].x]
		y = [data[0][0].y]
		z = [data[0][0].z]
		ax1.plot(x,y,z,'g',marker = 'o',label = "normal")
		ax1.plot(x,y,z,'b',marker = 'o',label = "false normal")
		ax1.plot(x,y,z,'r',marker = 'o',label = "anomaly")
		ax1.plot(x,y,z,'orange',marker = 'o',label = "false anomaly")
		ax1.plot(x,y,z,'pink',marker = 'o')
		ax1.legend()



		x = [data[1][0].x]
		y = [data[1][0].y]
		z = [data[1][0].z]
		ax2.plot(x,y,z,'g',marker = 'o',label = "normal")
		ax2.plot(x,y,z,'b',marker = 'o',label = "false normal")
		ax2.plot(x,y,z,'r',marker = 'o',label = "anomaly")
		ax2.plot(x,y,z,'orange',marker = 'o',label = "false anomaly")
		ax2.plot(x,y,z,'pink',marker = 'o')
		ax2.legend()

		
		x = [data[2][0].x]
		y = [data[2][0].y]
		z = [data[2][0].z]
		ax3.plot(x,y,z,'g',marker = 'o',label = "normal")
		ax3.plot(x,y,z,'b',marker = 'o',label = "false normal")
		ax3.plot(x,y,z,'r',marker = 'o',label = "anomaly")
		ax3.plot(x,y,z,'orange',marker = 'o',label = "false anomaly")
		ax3.plot(x,y,z,'pink',marker = 'o')
		ax3.legend()






		#printing cluster means of the 3 servers
		for i in range(0,3):
			printClusterMeans(i)

		numpoints = 0
		#Getting new data points from the servers and classifying them as normal or anomalous
		while(numpoints<1000):	
			numpoints += 1
			for i in range(0,3):
				(flag,point) = main(i)
				ret_type = get_cluster(point,i,flag)  #0-> normal, #1-> false normal, #2 -> anomalous, #3 -> false anomaly
				plt.figure(i+1)
			#	ax = fig.add_subplot(111,projection = '3d')
			#	ax = fig.add_subplot()
				#ax = plt.subplot(111)
				#print(ret_type)
				c = 'b'
				if ret_type == 0: #normal
					c = 'g'
				elif ret_type == 1: #false normal
					c = 'b'
				elif ret_type == 2: #anomaly
					c = 'r'
				else:
					c = 'orange' #false anomaly



				if i == 0:
					ax1.scatter(point.x, point.y, point.z, c=c, marker = 'o',zorder = 0)
				elif i == 1:
					ax2.scatter(point.x, point.y, point.z, c=c, marker = 'o',zorder = 0)
				else:
					ax3.scatter(point.x, point.y, point.z, c=c, marker = 'o',zorder = 0)
				plt.draw()
				plt.pause(0.0000000001)

		output = open("stats.csv","w")
		output.write("True normal,False normal,True anomaly,False anomaly, actual anomalous\n")
		output.write(str(counter[0]) + "," + str(counter[1]) + "," + str(counter[2]) + "," + str(counter[3]) + "," +str(anomalous_count))







