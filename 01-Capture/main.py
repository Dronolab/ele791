from UAVServer import Server
import time

if __name__ == "__main__":
    UAV_server = Server()
    UAV_server.SubProcessStart()
    while True:
        time.sleep(1)



