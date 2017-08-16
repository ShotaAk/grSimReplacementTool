#!/usr/bin/env  python
# -*- coding: utf-8 -*-

import sys
import socket
import netifaces
import time
import math
import toml
from include import grSim_Packet_pb2
from include import messages_robocup_ssl_wrapper_pb2

class Sender:
    def __init__(self):
        # initialize a socket
        self._addr = "127.0.0.1"
        self._port = 20012
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    def sendReplaceFromConfig(self, filepath):
        packet = grSim_Packet_pb2.grSim_Packet()

        data = toml.load(filepath)

        # set blue robots data
        robot_data = data["Blue_Robot"]
        for key_id in robot_data:
            robot_dict = robot_data[key_id]
            replace_robot = packet.replacement.robots.add()
            self.setReplacementRobotData(replace_robot, robot_dict, int(key_id), False)


        # set blue robots data
        robot_data = data["Yellow_Robot"]
        for key_id in robot_data:
            robot_dict = robot_data[key_id]
            replace_robot = packet.replacement.robots.add()
            self.setReplacementRobotData(replace_robot, robot_dict, int(key_id), True)

        # set ball data
        ball_dict = data["Ball"]
        replace_ball = packet.replacement.ball
        self.setReplacementBallData(replace_ball,ball_dict)

        # send packet
        message = packet.SerializeToString()
        self._socket.sendto(message,(self._addr,self._port))


    def setReplacementRobotData(self, replace_robot, robot_dict, robot_id, isYellow):
        replace_robot.id = robot_id
        replace_robot.yellowteam = isYellow
        replace_robot.x = robot_dict["x"]
        replace_robot.y = robot_dict["y"]
        replace_robot.dir = robot_dict["dir"]
        replace_robot.turnon = robot_dict["turnon"]


    def setReplacementBallData(self, replace_ball, ball_dict):
        replace_ball.x = ball_dict["x"]
        replace_ball.y = ball_dict["y"]
        replace_ball.vx = ball_dict["vx"]
        replace_ball.vy = ball_dict["vy"]


class RobotData:
    def __init__(self):
        self.robot_id = 0
        self.x = 0.0
        self.y = 0.0
        self.dir = 0.0
        self.turnon = True
        self.is_enable = False


class BallData:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.is_enable = False


class Receiver:
    def __init__(self):
        self._addr = "224.5.23.2"
        self._port = 10006
        self._collecting_time = 1.5

        # Create the socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.init_socket()

        # make protobuf instance
        self._ssl_wrapper = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()

        self._ball = BallData()
        self._blue_robots = []
        self._yellow_robots = []
        for i in range(6):
            self._blue_robots.append(RobotData())
            self._yellow_robots.append(RobotData())


    def init_socket(self):
        # Set some options to make it multicast-friendly
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        self._socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

        # Bind to the port
        self._socket.bind(("", self._port))

        # Detect local ip address and interfaces
        default_iface = "eth0"
        local_addr = "0.0.0.0"
        if default_iface in netifaces.interfaces():
            iface_data = netifaces.ifaddresses(default_iface)
            local_addr = iface_data.get(netifaces.AF_INET)[0]["addr"]
        else:
            for iface_name in netifaces.interfaces():
                iface_data = netifaces.ifaddresses(iface_name)
                addr = iface_data.get(netifaces.AF_INET)[0]["addr"]

                # Omit local loop back address
                if(addr != "127.0.0.1"):
                    local_addr = addr

        # Set some multicast options
        self._socket.setsockopt(
                socket.SOL_IP, 
                socket.IP_MULTICAST_IF, 
                socket.inet_aton(local_addr))
        self._socket.setsockopt(
                socket.SOL_IP, 
                socket.IP_ADD_MEMBERSHIP, 
                socket.inet_aton(self._addr) + socket.inet_aton(local_addr))
        self._socket.setblocking(False)


    def receive(self):
        try:
            buf = self._socket.recv(2*1024)
        except:
            return  None

        return  buf


    def logRepelacementToConfig(self, filepath):
        print "Receive vision packets for %f seconds" % self._collecting_time
        start_time = time.time()
        elapsed_time = 0.0
        buf = None
        while elapsed_time < self._collecting_time:
            elapsed_time = time.time() - start_time

            buf = self.receive()
            if buf is not None:
                self.decodePacket(buf)

        output_dict = self.convertDataToTOMLDict()
        toml.dump(output_dict, open(filepath, "w"))

    
    def decodePacket(self, buf):
        self._ssl_wrapper.ParseFromString(buf)

        for ball in self._ssl_wrapper.detection.balls:
            self._ball.x = ball.x
            self._ball.y = ball.y
            self._ball.vx = 0.0
            self._ball.vy = 0.0
            self._ball.is_enable = True

        for robot in self._ssl_wrapper.detection.robots_blue:
            current_id = robot.robot_id
            self._blue_robots[current_id].robot_id = current_id
            self._blue_robots[current_id].x = robot.x
            self._blue_robots[current_id].y = robot.y
            self._blue_robots[current_id].dir = robot.orientation
            self._blue_robots[current_id].turnon = True
            self._blue_robots[current_id].is_enable = True

        for robot in self._ssl_wrapper.detection.robots_yellow:
            current_id = robot.robot_id
            self._yellow_robots[current_id].robot_id = current_id
            self._yellow_robots[current_id].x = robot.x
            self._yellow_robots[current_id].y = robot.y
            self._yellow_robots[current_id].dir = robot.orientation
            self._yellow_robots[current_id].turnon = True
            self._yellow_robots[current_id].is_enable = True


    def convertDataToTOMLDict(self):
        ball_dict = {}
        ball_dict["x"] = self._ball.x * 0.001
        ball_dict["y"] = self._ball.y * 0.001
        ball_dict["vx"] = self._ball.vx
        ball_dict["vy"] = self._ball.vy

        blue_robot_dict = self.makeRobotDict(self._blue_robots)
        yellow_robot_dict = self.makeRobotDict(self._yellow_robots)

        output_dict = {}
        if self._ball.is_enable:
            output_dict["Ball"] = ball_dict
        output_dict["Blue_Robot"] = blue_robot_dict
        output_dict["Yellow_Robot"] = yellow_robot_dict

        return output_dict


    def makeRobotDict(self, robots):
        output_dict = {}
        for robot in robots:
            if robot.is_enable:
                robot_dict = {}
                robot_dict["x"] = robot.x * 0.001
                robot_dict["y"] = robot.y * 0.001
                robot_dict["dir"] = robot.dir * 180.0 / math.pi
                robot_dict["turnon"] = robot.turnon

                output_dict[str(robot.robot_id)] = robot_dict

        return output_dict


def parser():
    usage = 'Usage: python {} FILE [--set] [--log] [--help]'\
            .format(__file__)
    arguments = sys.argv
    if len(arguments) == 1:
        return usage, ""

    # Remove the first argument (file itself)
    arguments.pop(0)

    # Get argument file name
    fname = arguments[0]
    if fname.startswith('-'):
        return usage, ""

    # Extract option '-(somthing)'
    options = [option for option in arguments if option.startswith('-')]

    if '-h' in options or '--help' in options:
        return usage, ""
    if '-s' in options or '--set' in options:
        return "SET", fname
    if '-l' in options or '--log' in options:
        return "LOG", fname

    return usage, ""


if __name__=="__main__":
    sender = Sender()
    receiver = Receiver()

    result, filepath = parser()
    print result
    if result == "SET":
        sender.sendReplaceFromConfig(filepath)
    elif result == "LOG":
        receiver.logRepelacementToConfig(filepath)
    else:
        exit()

