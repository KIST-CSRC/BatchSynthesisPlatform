#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [py example simple] Robot Arm motion for doosan robot
# @author    Nayeon Kim (kny@kist.re.kr) // Hyuk Jun Yoo (yoohj9475@kist.re.kr)
# @version 1_2
# TEST 2021-09-23
# Test 2022-04-13

import socket
import os, sys 
import time
import json
from click import command
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from BaseUtils.Preprocess import PreprocessJSON
from BaseUtils.TCP_Node import BaseTCPNode

sys.dont_write_bytecode = True
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "common/imp")))  # get import path : DSR_ROBOT.py
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Robot_Arm")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) 

# for single robot
ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"
import DR_init
DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL
from DSR_ROBOT import *
from robot_teaching import location_dict
# Fundermental componant--------------------
# 

class ParameterRobot:
    """
    general Actuator IP, PORT, location dict, move_z

    :param self.WINDOWS1_HOST = '161.122.22.146'  # The server's hostname or IP address
    :param self.PORT_UV = 54011       # The port used by the UV server (54011)
    """
    def __init__(self):
        self.Robot_info= {
            "HOST_ROBOT" : "161.122.22.174",
            "PORT_ROBOT" : 54011
        }
      
class Robot_Class(object):

    def __init__(self, logger_obj, device_name="DS_B"):
        ParameterRobot.__init__(self)
        BaseTCPNode.__init__(self)
        PreprocessJSON().__init__()
        self.logger_obj = logger_obj
        self.device_name = device_name

    def _callServer_Robot(self, command_byte):
        res_msg = self.callServer(self.Robot_info["HOST_ROBOT"], self.Robot_info["PORT+ROBOT"], command_byte)

    def hello(self):

        debug_device_name = "{} ({})".format(self.device_name, "hello")

        command_byte = str.encode("{},{}".format("hello", "status"))
        res_msg=self._callServer_Robot(command_byte)

        self.logger_obj.debug(device_name=debug_device_name, debug_msg=res_msg)

        return res_msg

    def getRobotData(self, client_socket, action_type, mode_type="virtual"):
        """
        get Absorbance data using TCP/IP (socket)
        
        :param client_socket (str): input sockect object (main computer)
        :param action_type (str): chemical element (Ag,Au....)
        :param mode_type="virtual" (str): set virtual or real mode

        :return res_msg (bool): response_message --> [UV] : ~~~
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)
        self.logger_obj.debug(device_name=debug_device_name, debug_msg="start get {} data".format(action_type))

        # if mode_type == "real":
        command_byte = str.encode("{},{}".format(action_type, "NP"))

        # get json file name through Robot server
        file_name_decoded=self._callServer_Robot(command_byte)

        # open json content using open function
        total_json = self.openJSON(filename=file_name_decoded)
        ourbyte = self.encodeJSON(json_obj=total_json)

        # send big json file using parsing
        if len(ourbyte) > self.BUFF_SIZE:
            self.sendTotalJSON(client_socket=client_socket, ourbyte=ourbyte)
        else:
            client_socket.sendall(json.dumps(total_json).encode("utf-8"))
        
        # send finish message to main computer
        time.sleep(3)
        finish_msg="finish"
        client_socket.sendall(finish_msg.encode())

        self.logger_obj.debug(device_name=debug_device_name, debug_msg=finish_msg)
        return_res_msg="[{}] : {}".format(debug_device_name, finish_msg)
        return return_res_msg

def shutdown():
    print("shutdown time!")
    print("shutdown time!")
    print("shutdown time!")

    pub_stop.publish(stop_mode=STOP_TYPE_QUICK)
    return 0


def msgRobotState_cb(msg):
    msgRobotState_cb.count += 1

    if 0 == (msgRobotState_cb.count % 100000):
        rospy.loginfo("________ ROBOT STATUS ________")
        print("  robot_state           : %d" % msg.robot_state)
        print("  robot_state_str       : %s" % msg.robot_state_str)
        print("  actual_mode           : %d" % msg.actual_mode)
        print("  actual_space          : %d" % msg.actual_space)
        print("  current_posj          : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.current_posj[0], msg.current_posj[1], msg.current_posj[2], msg.current_posj[3], msg.current_posj[4],
            msg.current_posj[5]))
        print("  current_velj          : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.current_velj[0], msg.current_velj[1], msg.current_velj[2], msg.current_velj[3], msg.current_velj[4],
            msg.current_velj[5]))
        print("  joint_abs             : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.joint_abs[0], msg.joint_abs[1], msg.joint_abs[2], msg.joint_abs[3], msg.joint_abs[4], msg.joint_abs[5]))
        print("  joint_err             : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.joint_err[0], msg.joint_err[1], msg.joint_err[2], msg.joint_err[3], msg.joint_err[4], msg.joint_err[5]))
        print("  target_posj           : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.target_posj[0], msg.target_posj[1], msg.target_posj[2], msg.target_posj[3], msg.target_posj[4],
            msg.target_posj[5]))
        print("  target_velj           : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.target_velj[0], msg.target_velj[1], msg.target_velj[2], msg.target_velj[3], msg.target_velj[4],
            msg.target_velj[5]))
        print("  current_posx          : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.current_posx[0], msg.current_posx[1], msg.current_posx[2], msg.current_posx[3], msg.current_posx[4],
            msg.current_posx[5]))
        print("  current_velx          : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.current_velx[0], msg.current_velx[1], msg.current_velx[2], msg.current_velx[3], msg.current_velx[4],
            msg.current_velx[5]))
        print("  task_err              : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.task_err[0], msg.task_err[1], msg.task_err[2], msg.task_err[3], msg.task_err[4], msg.task_err[5]))
        print("  solution_space        : %d" % msg.solution_space)
        sys.stdout.write("  rotation_matrix       : ")
        for i in range(0, 3):
            sys.stdout.write("dim : [%d]" % i)
            sys.stdout.write("  [ ")
            for j in range(0, 3):
                sys.stdout.write("%d " % msg.rotation_matrix[i].data[j])
            sys.stdout.write("] ")
        print  ##end line
        print("  dynamic_tor           : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.dynamic_tor[0], msg.dynamic_tor[1], msg.dynamic_tor[2], msg.dynamic_tor[3], msg.dynamic_tor[4],
            msg.dynamic_tor[5]))
        print("  actual_jts            : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.actual_jts[0], msg.actual_jts[1], msg.actual_jts[2], msg.actual_jts[3], msg.actual_jts[4],
            msg.actual_jts[5]))
        print("  actual_ejt            : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.actual_ejt[0], msg.actual_ejt[1], msg.actual_ejt[2], msg.actual_ejt[3], msg.actual_ejt[4],
            msg.actual_ejt[5]))
        print("  actual_ett            : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.actual_ett[0], msg.actual_ett[1], msg.actual_ett[2], msg.actual_ett[3], msg.actual_ett[4],
            msg.actual_ett[5]))
        print("  sync_time             : %7.3f" % msg.sync_time)
        print("  actual_bk             : %d %d %d %d %d %d" % (
            msg.actual_bk[0], msg.actual_bk[1], msg.actual_bk[2], msg.actual_bk[3], msg.actual_bk[4], msg.actual_bk[5]))
        print("  actual_bt             : %d %d %d %d %d " % (
            msg.actual_bt[0], msg.actual_bt[1], msg.actual_bt[2], msg.actual_bt[3], msg.actual_bt[4]))
        print("  actual_mc             : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.actual_mc[0], msg.actual_mc[1], msg.actual_mc[2], msg.actual_mc[3], msg.actual_mc[4], msg.actual_mc[5]))
        print("  actual_mt             : %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f" % (
            msg.actual_mt[0], msg.actual_mt[1], msg.actual_mt[2], msg.actual_mt[3], msg.actual_mt[4], msg.actual_mt[5]))

        # print digital i/o
        sys.stdout.write("  ctrlbox_digital_input : ")
        for i in range(0, 16):
            sys.stdout.write("%d " % msg.ctrlbox_digital_input[i])
        print  ##end line
        sys.stdout.write("  ctrlbox_digital_output: ")
        for i in range(0, 16):
            sys.stdout.write("%d " % msg.ctrlbox_digital_output[i])
        print 
        sys.stdout.write("  flange_digital_input  : ")
        for i in range(0, 6):
            sys.stdout.write("%d " % msg.flange_digital_input[i])
        print
        sys.stdout.write("  flange_digital_output : ")
        for i in range(0, 6):
            sys.stdout.write("%d " % msg.flange_digital_output[i])
        print
        # print modbus i/o
        sys.stdout.write("  modbus_state          : ")
        if len(msg.modbus_state) > 0:
            for i in range(0, len(msg.modbus_state)):
                sys.stdout.write("[" + msg.modbus_state[i].modbus_symbol)
                sys.stdout.write(", %d] " % msg.modbus_state[i].modbus_value)
        print

        print("  access_control        : %d" % msg.access_control)
        print("  homming_completed     : %d" % msg.homming_completed)
        print("  tp_initialized        : %d" % msg.tp_initialized)
        print("  mastering_need        : %d" % msg.mastering_need)
        print("  drl_stopped           : %d" % msg.drl_stopped)
        print("  disconnected          : %d" % msg.disconnected)

def Robot_initialize():
    rospy.init_node('single_robot_simple_py', log_level=rospy.ERROR)
    rospy.on_shutdown(shutdown)
    global set_robot_mode
    set_robot_mode = rospy.ServiceProxy('/' + ROBOT_ID + ROBOT_MODEL + '/system/set_robot_mode', SetRobotMode)
    t1 = threading.Thread(target=thread_subscriber)
    t1.daemon = True
    t1.start()

    global pub_stop
    pub_stop = rospy.Publisher('/' + ROBOT_ID + ROBOT_MODEL + '/stop', RobotStop, queue_size=10)

    set_robot_mode(ROBOT_MODE_AUTONOMOUS)

    # global parameter
    set_velx(2500, 800.63)  # set global task speed: 30(mm/sec), 20(deg/sec)
    set_accx(100, 300)  # set global task accel: 60(mm/sec2), 40(deg/sec2)

    # openGripper()
    # closeGripper(action_type="Vial")

msgRobotState_cb.count = 0

def get_status():
    robot_position = get_current_posx()
    return robot_position

def thread_subscriber():
    rospy.Subscriber('/' + ROBOT_ID + ROBOT_MODEL + '/state', RobotState, msgRobotState_cb)
    rospy.spin()
    # rospy.spinner(2)


def openGripper(action_type="Vial"):
    """
    ONROBOT_TARGET_FORCE_1: 0
    ONROBOT_TARGET_WIDTH_1: 0 (600 == 60mm)
    ONROBOT_CONTROL_1: 1 (1 == action)
    ONROBOT_ACTUAL_DEPTH_1: 211
    ONROBOT_ACTUAL_REL_DEPTH_1: 211
    ONROBOT_ACTUAL_WIDTH_1: 918
    ONROBOT_STATUS_1: 0
    """
    if action_type == "Vial":
        set_modbus_output("ONROBOT_TARGET_WIDTH_1", 500) 
        set_modbus_output("ONROBOT_TARGET_FORCE_1", 400)
        set_modbus_output("ONROBOT_CONTROL_1", 1)

    elif action_type == "Cuvette":
        set_modbus_output("ONROBOT_TARGET_WIDTH_1", 400)
        set_modbus_output("ONROBOT_TARGET_FORCE_1", 200)
        set_modbus_output("ONROBOT_CONTROL_1", 1)


def closeGripper(action_type="Vial"):
    if action_type == "Vial":
        set_modbus_output("ONROBOT_TARGET_WIDTH_1", 350)
        set_modbus_output("ONROBOT_TARGET_FORCE_1", 400)
        set_modbus_output("ONROBOT_CONTROL_1", 1)

    elif action_type == "Cuvette":
        set_modbus_output("ONROBOT_TARGET_WIDTH_1", 200)
        set_modbus_output("ONROBOT_TARGET_FORCE_1", 200)
        set_modbus_output("ONROBOT_CONTROL_1", 1)

def pick(approach, leave, object_type):
    '''
    pick (bird coordination(before pick) -> approach -> close gripper -> leave -> bird coordination)
    
    :param approach (int): approch distance 
    :param leave (int): leave distance  
    :param object_type (str): object type for gripper distance 
        ex) Vial, Cuvette
    '''
    movel(approach, vel = 500, acc = 50, ref = DR_TOOL)
    closeGripper(action_type = object_type)
    movel(leave, vel = 500, acc = 50, ref = DR_TOOL)

def place(approach, leave, object_type):
    '''
    place (bird coordination(before pick) -> approach -> open gripper -> leave -> bird coordination)
    
    :param approach (int): approch distance 
    :param leave (int): leave distance  
    :param object_type (str): object type for gripper distance 
        ex) Vial, Cuvette
    '''
    movel(approach, vel = 500, acc = 50, ref = DR_TOOL)
    openGripper(action_type = object_type)
    movel(leave, vel = 500, acc = 50, ref = DR_TOOL)

def move_HOME(temp_info_dict):
    temp_info_dict=location_dict["move_HOME"]
    movel(temp_info_dict["location_list"][0], vel=temp_info_dict['vel']['general'], acc=temp_info_dict["acc"]["general"])
    
def move_before_pick_point(temp_location_dict):
    '''
    move before pick point

    :temp_location_dict (list): sequence of each action
        ex) storage_empty_to_stirrer_list = [[pos_XYZ, pos_storage, storage_empty_center], 
                            storage_empty_pick_1,
                            storage_empty_pick_2, 
                            [pos_storage, pos_XYZ, stirrer_center],
                            stirrer_place_1,
                            stirrer_place_2, 
                            [stirrer_center, pos_XYZ]
                            ]
        -> ONLY USE [pos_XYZ, pos_storage, storage_empty_center] part.
    '''
    for i in range(len(temp_location_dict["location_list"][0])):
        movel(temp_location_dict["location_list"][0][i], vel = temp_location_dict["vel"]["general"], acc = temp_location_dict["acc"]["general"])
    
def move_place_point_during_picking_vial(temp_location_dict):
    '''
    move place point during picking vial 

    :temp_location_dict (list): sequence of each action
        ex) storage_empty_to_stirrer_list = [[pos_XYZ, pos_storage, storage_empty_center], 
                            storage_empty_pick_1,
                            storage_empty_pick_2, 
                            [pos_storage, pos_XYZ, stirrer_center],
                            stirrer_place_1,
                            stirrer_place_2, 
                            [stirrer_center, pos_XYZ]
                            ]
        -> ONLY USE [pos_storage, pos_XYZ, stirrer_center] part.
    '''
    for i in range(len(temp_location_dict["location_list"][3])):
        movel(temp_location_dict["location_list"][3][i], vel=temp_location_dict['vel']['general'], acc = temp_location_dict["acc"]['general'])

def move_ending_point(temp_location_dict):
    '''
    move ending point to finish action 

    :temp_location_dict (list): sequence of each action
        ex) storage_empty_to_stirrer_list = [[pos_XYZ, pos_storage, storage_empty_center], 
                            storage_empty_pick_1,
                            storage_empty_pick_2, 
                            [pos_storage, pos_XYZ, stirrer_center],
                            stirrer_place_1,
                            stirrer_place_2, 
                            [stirrer_center, pos_XYZ]
                            ]
        -> ONLY USE [stirrer_center, pos_XYZ] part.
    '''
    for i in range(len(temp_location_dict["location_list"][6])):
        movel(temp_location_dict["location_list"][6][i], vel=temp_location_dict['vel']['general'], acc = temp_location_dict["acc"]['general'])

def pick_and_place(NodeLogger, pick_num, place_num, action_type='storage_empty_to_stirrer', mode_type="virtual"):

    """
        Pick and place function for moving object with DOOSAN robot

        :param NodeLogger (MasterLogger): MasterLogger object to control log message
        :param pick_num (int) : pick number of each hardware location (0-7) 
        :param place_num (int) : place number of each hardware loaction (0-7)
        :param action_type (str) : Key of input_location_dict. 
            ex) storage_empty_to_stirrer
                stirrer_to_holder
                holder_to_storage_filled
                cuvette_storage_to_cuvette_holder
                cuvette_holder_to_UV
                UV_to_cuvette_storage
        :return: None
        
        temp_info_dict = 
        {
            "location_list" : Storage_empty_to_Stirrer_list,
            "pick_loc_list" : storage_empty_list,
            "place_loc_list" : stirrer_list,
            "object_type" : 'Vial',
            "ref" : "DR_BASE",
            "vel":{
                "general":250,
                "radious":80
            },
            "acc":{
                "general":1,
                "radious":332
            }
        }
    """
    temp_info_dict=location_dict[action_type]
    device_name = "{} ({})".format("Doosan Arm m0609",mode_type)
    # change later
    if mode_type=="real":
        openGripper(action_type = temp_info_dict['object_type'])
    msg = "Pick and place : Gripper is opened."
    NodeLogger.debug(device_name=device_name, debug_msg=msg)

    if mode_type=="real":
        move_before_pick_point(temp_info_dict) # move before pick point
    msg = "Pick and place : Move before pick point."
    NodeLogger.debug(device_name=device_name, debug_msg=msg)

    if mode_type=="real":
        movel(temp_info_dict["pick_loc_list"][pick_num], vel=temp_info_dict['vel']['general'], acc = temp_info_dict["acc"]['general'])
    msg = "Pick and place : Move pick point."
    NodeLogger.debug(device_name=device_name, debug_msg=msg)

    if mode_type=="real":
        pick(temp_info_dict["location_list"][1], temp_info_dict["location_list"][2], object_type=temp_info_dict["object_type"]) # go below -> pick -> go up
    msg = "Pick and place : Pick."
    NodeLogger.debug(device_name=device_name, debug_msg=msg)

    if mode_type=="real":
        move_place_point_during_picking_vial(temp_info_dict) # move place point during picking vial
    msg = "Pick and place : Move before place point during picking vial."
    NodeLogger.debug(device_name=device_name, debug_msg=msg)

    if mode_type=="real":
        movel(temp_info_dict["place_loc_list"][place_num], vel=temp_info_dict['vel']['general'], acc = temp_info_dict["acc"]['general'])
    msg = "Pick and place : Move place point during picking vial."
    NodeLogger.debug(device_name=device_name, debug_msg=msg)

    if mode_type=="real":
        place(temp_info_dict["location_list"][4], temp_info_dict["location_list"][5], object_type=temp_info_dict["object_type"]) # go below -> place -> go up
    msg = "Pick and place : Place."
    NodeLogger.debug(device_name=device_name, debug_msg=msg)

    if mode_type=="real":
        move_ending_point(temp_info_dict) # move ending point
    msg = "Pick and place : Move home"
    NodeLogger.debug(device_name=device_name, debug_msg=msg)

    msg = "{0} : {1}_{2} -> {3}_{4}".format(action_type, temp_info_dict['msg']['from'], pick_num, temp_info_dict['msg']['to'], place_num)
    NodeLogger.debug(device_name=device_name, debug_msg=msg)

    return msg

# real motion -------------------------------------------------------------------------------------------------------------------------------------

def move_Storage_empty_to_Stirrer(NodeLogger, cycle_num, place_num, mode_type="virtual"):
    '''
    move (storage -> Strrier) with DOOSAN robot

    :param NodeLogger (MasterLogger): MasterLogger object to control log message
    :param cycle_num (int): cycle number of batch system(chemical storage, stirrer, cuvette storage)
    :param place_num (int): place number of each vessel loaction (0-7)
    :param mode_type (str): "virtual" (str): set mode type --> real, virtual
    '''

    pick_and_place(NodeLogger, (cycle_num)//2, place_num, action_type='storage_empty_to_stirrer', mode_type=mode_type)

def move_Stirrer_to_Holder(NodeLogger, place_num, mode_type="virtual"):
    '''
    move (Stirrer -> Holder) with DOOSAN robot

    :param NodeLogger (MasterLogger): MasterLogger object to control log message
    :param place_num (int): place number of each vessel loaction (0-7)
    :param mode_type (str): "virtual" (str): set mode type --> real, virtual
    '''
    pick_and_place(NodeLogger, place_num, place_num, action_type='stirrer_to_holder', mode_type=mode_type)

def move_Holder_to_Storage_filled(NodeLogger, cycle_num, pick_num, mode_type="virtual"):
    '''
    move (Holder -> Stroage filled) with DOOSAN robot

    :param NodeLogger (MasterLogger): MasterLogger object to control log message
    :param cycle_num (int): cycle number of batch system(chemical storage, stirrer, cuvette storage)
    :param pick_num_num (int): pick number of each vessel loaction (0-7)
    :param mode_type (str): "virtual" (str): set mode type --> real, virtual
    '''
    pick_and_place(NodeLogger, pick_num, (cycle_num)//2, action_type='holder_to_storage_filled', mode_type=mode_type)


def move_Stirrer_to_Storage_filled(NodeLogger, cycle_num, pick_num, mode_type="virtual"):
    '''
    move (Holder -> Stroage filled) with DOOSAN robot

    :param NodeLogger (MasterLogger): MasterLogger object to control log message
    :param cycle_num (int): cycle number of batch system(chemical storage, stirrer, cuvette storage)
    :param pick_num_num (int): pick number of each vessel loaction (0-7)
    :param mode_type (str): "virtual" (str): set mode type --> real, virtual
    '''
    pick_and_place(NodeLogger, pick_num, (cycle_num)//2, action_type='holder_to_storage_filled', mode_type=mode_type)    

def move_Cuvette_storage_to_Cuvette_holder(NodeLogger, cycle_num, pick_num, mode_type="virtual"):
    """
    This function has 8 action which move 8 cuvette to each cuvette holder.

    :param NodeLogger (MasterLogger): MasterLogger object to control log message
    :param cycle_num (int): cycle number of batch system(chemical storage, stirrer, cuvette storage)
    :param pick_num_num (int): pick number of each vessel loaction (0-7)   
    :param mode_type (str): "virtual" (str): set mode type --> real, virtual
    """
    pick_and_place(NodeLogger, (cycle_num)*8+pick_num, pick_num, action_type='cuvette_storage_to_cuvette_holder',mode_type=mode_type)
    
def move_Cuvette_holder_to_UV(NodeLogger, pick_num, mode_type="virtual"):
    """
    This function has 1 action which move 1 cuvette to each UV holder.

    :param NodeLogger (MasterLogger): MasterLogger object to control log message
    :param pick_num_num (int): pick number of each vessel loaction (0-7)   
    :param mode_type (str): "virtual" (str): set mode type --> real, virtual
    """
    pick_and_place(NodeLogger, pick_num, 0, action_type='cuvette_holder_to_UV',mode_type=mode_type)

def move_UV_to_Cuvette_storage(NodeLogger, cycle_num, place_num, mode_type="virtual"):
    """
    This function has 1 action which move 1 cuvette to each cuvette storage.

    :param NodeLogger (MasterLogger): MasterLogger object to control log message
    :param cycle_num (int): cycle number of batch system(chemical storage, stirrer, cuvette storage)
    :param place_num_num (int): place number of each vessel loaction (0-7)   
    :param mode_type (str): "virtual" (str): set mode type --> real, virtual
    """
    pick_and_place(NodeLogger, 0, (cycle_num)*8+place_num, action_type='UV_to_cuvette_storage',mode_type=mode_type)

def TEST_move_one_cycle(NodeLogger,cycle_num, mode_type="virtual"):
    # tcp_obj=TCP_Class()

    # msg = 'Testing whole action (DOOSAN robot + vial stroage) is started : cycle number is {}.'.format(cycle_num)
    # NodeLogger.info(part_name='SelfdrivingLab', info_msg="Start Robot Queue : "+msg)

    # command_bytes=str.encode("{}/{}/{}".format("STORAGE",(cycle_num)//2+1, mode_type))
    # res_msg=tcp_obj.callServer_STORAGE(command_byte=command_bytes)
    time.sleep(2)
    # for action_idx in range(1):
    #     move_Storage_empty_to_Stirrer(NodeLogger, cycle_num=cycle_num, place_num=action_idx, mode_type=mode_type)
    # for action_idx in range(8):
    #     move_Stirrer_to_Holder(NodeLogger, cycle_num=cycle_num, place_num=action_idx, mode_type=mode_type)


    for action_idx in range(8):
        move_Cuvette_storage_to_Cuvette_holder(NodeLogger, cycle_num=cycle_num, pick_num=action_idx, mode_type=mode_type)
    # for each_vial_loc in range(8):    
    #     move_Cuvette_holder_to_UV(NodeLogger, pick_num=each_vial_loc, mode_type=mode_type)
        # move_UV_to_Cuvette_storage(NodeLogger, cycle_num=cycle_num, place_num=each_vial_loc, mode_type=mode_type)

    # time.sleep(2)
    # command_bytes=str.encode("{}/{}/{}".format("STORAGE",(cycle_num)//2+6,mode_type))
    # res_msg=tcp_obj.callServer_STORAGE(command_byte=command_bytes)  
    # for action_idx in range(1):
    #     move_Holder_to_Storage_filled(NodeLogger, cycle_num=cycle_num, pick_num=action_idx, mode_type=mode_type)

# if __name__ == "__main__":
#     # robot center setting-----------------------
#     openGripper(action_type = 'Vial')
#     pos_XYZ = posx(8.240, 258.440, 353.510, 90, -180, -90)
#     pos_storage = posx(-277.030, 115.450, 487.380, 0, -180, -270)
#     pos_anaylsis = posx(257.620, 15.140, 359.070, 180, -180, 90)
    
#     meta = {
#             "metadata":
#                         {
#                             "subject":"Find lambda_max",
#                             "researcherGroup":"KIST_CSRC",
#                             "researcherName":"HJ",
#                             "researcherId":"yoohj9475@kist.re.kr",
#                             "researcherPwd":"1234",
#                             "element":"Ag",
#                             "experimentType":"autonomous",
#                             "logLevel":"INFO",
#                             "modeType":"real",
#                             "saveDirPath":"/home/sdl-pc/catkin_ws/src/doosan-robot",
#                             "totalIterNum":4,
#                             "batchSize":8
#                         }
#             }

#     from Log.Logging_Class import NodeLogger
#     NodeLogger=NodeLogger(platform_name="Batch Synthesis Server", setLevel="DEBUG", SAVE_DIR_PATH="C:/Users/KIST/PycharmProjects/BatchPlatform")

#     Robot_initialize()

#     # motion------------------------------------``

#     # status = get_status()
#     # print(status)
#     openGripper()
#     for i in range (0,10):
#         TEST_move_one_cycle(NodeLogger,cycle_num=i,mode_type="real")



if __name__ == "__main__":

    import os, sys
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../Log")))  # get import path : Logging_Class.py
    from Log.Logging_Class import NodeLogger
    # NodeLogger=NodeLogger(platform_name="Robot Platform", setLevel="DEBUG", SAVE_DIR_PATH="C:/Users/KIST/PycharmProjects/BatchPlatform")
    log_obj=NodeLogger(platform_name="RobotArm Server", setLevel="DEBUG",SAVE_DIR_PATH="C:/Users/KIST/PycharmProjects/BatchPlatform")
    # Robot_initialize()
    robot_obj=Robot_Class(logger_obj=log_obj, device_name="DS_B")
    # NodeLogger.getAbs_data()
    for i in range(2):
        TEST_move_one_cycle(NodeLogger=log_obj,cycle_num=i,mode_type="real")
    