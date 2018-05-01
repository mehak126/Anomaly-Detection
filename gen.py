import socket
import select
import sys
import math
import fractions
import random

serverPort = 12345
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind(('',serverPort))

def main():
	count = 0 #to keep count of number of times data has been sent so far
	characteristic_ratios = [[0.33,0.33,0.33], [0.6,0.3,0.1], [0.2,0.1,0.4]] #0-> file, 1-> jpg, 2-> vid
	rng = 5.0 #max range percentage of data around the characteristic ratios
	err = 25.0 #error percentage of anomalous data

	serverSocket.listen(1)
	print ('The server is ready')
	ratio = [0,0,0]

	while 1:
		connectionSocket, addr = serverSocket.accept()

		sentence = connectionSocket.recv(1024)

		if sentence == 'Send ftp data':
			print("Sending data to client " + str(addr))
			count += 1

			num = random.randint(0,2)
			send_anomalous = random.randint(0,100)

			if (count>1000) and (send_anomalous>70): #sending anomalous data with a probability of 30%
				data_ftp = "1"
				data_jpg = "1"
				data_vid = "1"

				

				for i in range(3):
					error = random.uniform(rng*1.05,err)
					exp = random.randint(0,1)
				#	ratio[i] = (characteristic_ratios[num][i]+((pow(-1,exp)*(error/100))*characteristic_ratios[num][i])) * 
					ratio[i] = characteristic_ratios[num][i]+((pow(-1,exp)*(error/100))*characteristic_ratios[num][i])
			
			elif (count>1000) and (send_anomalous<=70):
				data_ftp = "0"
				data_jpg = "0"
				data_vid = "0"
				
				

				for i in range(3):
					r = random.uniform(0,rng*1.05)
					exp = random.randint(0,1)
					ratio[i] = characteristic_ratios[num][i]+((pow(-1,exp)*(r/100))*characteristic_ratios[num][i])


			else: #randomly choosing one of the three characteristic ratios
				data_ftp = "0"
				data_jpg = "0"
				data_vid = "0"
				
				

				for i in range(3):
					r = random.uniform(0,rng)
					exp = random.randint(0,1)
					ratio[i] = (characteristic_ratios[num][i]+((pow(-1,exp)*(r/100))*characteristic_ratios[num][i]))	

			
			# print("ratio = ")
			# print(ratio)

			data_vid0 = get_vid()
			data_ftp0 = get_ftp()
			data_jpg0 = get_jpg()



			#appending bytes of each of the files to get the file size in the appropriate ratio
			for i in range(int(ratio[0]*1000)):
				data_ftp += data_ftp0[i]

			for i in range(int(ratio[1]*1000)):
				data_jpg += data_jpg0[i]

			for i in range(int(ratio[2]*1000)):
				data_vid += data_vid0[i]

			connectionSocket.send(data_ftp)
			connectionSocket.close()			

		if sentence == 'Send jpg data':
			connectionSocket.send(data_jpg)
			connectionSocket.close()

		if sentence == 'Send video data':
			connectionSocket.send(data_vid)
			connectionSocket.close()		

def get_ftp(): #reading and storing bytes of the text file
	ftp_file = open('README','rb')
	data_ftp = ftp_file.read()
	ftp_file.close()

	return data_ftp

def get_jpg(): #reading and storing bytes of the image file
	image = open("image3.png","rb")
	data_jpg = image.read()

	return data_jpg


def get_vid(): #reading and storing bytes of the byte file
	video = open("video2.mp4","rb")
	data_vid = video.read()

	return data_vid


if __name__ == '__main__':
		main()
