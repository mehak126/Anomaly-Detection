import socket
import sys
import math
from copy import deepcopy
import threading
import random
#import subprocess
import time


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


n = 500 #initial cluster points for each server
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


def main(server_id): #function which sets up a TCP connection with the server specified by the argument server_id and receives data from it
	
	#setting the server IP and Port for the TCP connection according to the id
	if server_id == 0:
		serverName = '10.184.13.145'
		serverPort = 12345

	elif server_id == 1:
		serverName = '10.184.13.145'
		serverPort = 12346

	else:
		serverName = '10.184.13.145'
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
	ftp_size = sys.getsizeof(ftp_data)
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
	jpg_size = sys.getsizeof(jpg_data)
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
	vid_size = sys.getsizeof(vid_data)
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

	return Coordinate(ratio[0],ratio[1],ratio[2],k)


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

		point = random.uniform(0,1)	'''We have now chosen a random point between 0 and 1. We will see the position in temp in whose range we will find this point. 
						This is as good as choosing a point at random, in a distribution poportional to distance squared.
						'''
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

def get_cluster(point,server): #Function to get cluster of the new data point and flag it as normal or anomalous

	min_dist = float('inf')
	anomalous = True

	for i in range(len(means[server])):
		if calc_distance(point, means[server][i]) <= (max_dist[server][i]*1.1) : #checking if the point lies within 10% of the farthest point from the cluster center
			anomalous = False
			if(calc_distance(point, means[server][i]) < min_dist):
				point.c = i;
				min_dist = calc_distance(point, means[server][i])


	if anomalous == True :
		print("\nAnomalous data detected in server " + str(server) + "\n")
		#turning on the appropriate leds of the raspberry pi according to the server
		if server == 0:
			subprocess.call('echo 1 | sudo tee /sys/class/leds/led1/brightness', shell = True)
		elif server == 1:
			subprocess.call('echo 1 | sudo tee /sys/class/leds/led0/brightness', shell = True)
		else:
			subprocess.call('echo 1 | sudo tee /sys/class/leds/led0/brightness', shell = True)
			subprocess.call('echo 1 | sudo tee /sys/class/leds/led1/brightness', shell = True)
		time.sleep(2)



	else : #updating cluster center with the new point included
		subprocess.call('echo 0 | sudo tee /sys/class/leds/led0/brightness', shell = True)
		subprocess.call('echo 0 | sudo tee /sys/class/leds/led1/brightness', shell = True)
		data[server].append(point)
		updateMeans(server)
			

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
		subprocess.call('echo 0 | sudo tee /sys/class/leds/led0/brightness', shell = True)
		subprocess.call('echo 0 | sudo tee /sys/class/leds/led1/brightness', shell = True)

		#getting 'n' points for initial clustering from the 3 servers
		for i in range(0,3):
			for j in range(n):
				point = main(i)

		#Forming clusters of the initial points of each server
		kmeans(characteristic_points_s1,0);
		kmeans(characteristic_points_s2,1);
		kmeans(characteristic_points_s3,2);

		#printing cluster means of the 3 servers
		for i in range(0,3):
			printClusterMeans(i)

		#Getting new data points from the servers and classifying them as normal or anomalous
		while(1):
		
			for i in range(0,3):
				point = main(i)
				get_cluster(point,i)







