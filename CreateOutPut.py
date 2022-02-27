import os
import math
import operator
import json
from pydoc import doc
from time import sleep

# 导入地图右上角坐标
map_upper_right_x = 4958
map_upper_right_y = 3638

# 导入地图左下角坐标
map_bottom_left_x = 362
map_bottom_left_y = 362

# 处理地图参数,将其百位数取整以方便路径规划
map_upper_right_x = int(map_upper_right_x/100)*100
map_upper_right_y = int(map_upper_right_y/100)*100
map_bottom_left_x = math.ceil(map_bottom_left_x/100)*100
map_bottom_left_y = math.ceil(map_bottom_left_y/100)*100

# 相机坐标
camera_x = map_bottom_left_x
camera_y = map_bottom_left_y

# 相机坐标序号，从1开始，没有上限，来表示有多少个点
camera_id = 1

# 这里的z不能单纯看作是无人机高度，但为方便理解在这里依然可以看作是拍摄高度
map_lower = 200
map_top = 700



# 以45°为一组，在现实中，只需要与墙面成45°角度，即可只用拍摄四次，是为了减少数据量。
# 但由于我需要尽可能多的照片对集群进行压测，因此需要以45°为分割遍历所有的角度。
# 即-180、-135、-90、45、0、45、90、135、180
# 由于python变量不能用负号，因此我在后面用math的方法来表示负号。
# rotation_angle为相机的旋转角度
r1_180 = 3.1415927410125732
r1_135 = 2.356194496154785
r1_90 = 1.5707963705062866
r1_45 = 0.7853981852531433
r1_0 = 0
rotation_angle = operator.neg(r1_180)

# 空三建模需要正视与倾斜摄影两种照片，为简化拍摄参数R2仅分为90°与45°之分。但因为ra的bug导致无法完全为90°
# 下面为R2的两种取值，facing_photo只需要拍摄一次，tilt_photo在需要拍摄四次
r2_90 = 89
r2_45 = 45
camera_ground_angle = r2_45

# R3为地面旋转的角度，默认为0
r3_ground = 0

# 摄像机到达该节点时的时间，方便控制摄像机组件进行控制速度。这里的摄像机时间不能看作单纯的1s，而是游戏单位时间
# 在这里也写入摄像机的移速，默认是100单位坐标/s，调试的时候速度加快
camera_time = 0
camera_speed = 400

# 横向x是一个端点到另一个端点不用进行切割，仅仅需要对纵向进行切割,x_split始终为1
# x/y_split为分割时x/y轴被切割了多少段，最小值为1，即只有一段。
# 根据教程内的视频来看，航拍软件路径规划并不会强迫起始点与终点在对称的位置。
# 这里最好可以自动计算，第一版我手动切分即可。
# 根据地图y轴差值进行自动切割
x_split = 1
y_split = 1

# 计算为完美空三所需切割的数量
# 由于根据拿尺量，小地图的y轴是50单位，90°视角的y轴是6单位，则最小视角下的物理宽度是(3600-400)/50*6=384
# 计算结果向上取整
y_split = math.ceil((map_upper_right_y-map_bottom_left_y)/384)*2-1

print ("需要切分的区块数量为:" + str(y_split))

# x，y轴每次增加的数值
x_add = int((map_upper_right_x-map_bottom_left_x)/x_split)
y_add = int((map_upper_right_y-map_bottom_left_y)/y_split)

# x,y轴每次位移时所需时长
x_add_time = int(x_add/camera_speed)
y_add_time = int(y_add/camera_speed)


# 摄像机参数模板
# 此参数可以作为一种列表进行存储，为json的animations的值
# [0,{"label": "upper right","r1": 0,"r2": 45,"r3": 0,"x": 4900,"y": 3600,"z": 700}]

# 开始生成路径点坐标、为节省内存，将同时遍历两种R2的数值、r1角度
# 共计生成航线1+9=10次
# 由于数值不大，因此可以在内存进行组合后写入文件内。
# 后期如果需要优化，每生成一个角度、高度的航路后写入一次硬盘，这样可以优化内存占用。
# 还可以将这些分离开来，只不过嵌套函数在这种级别的脚本多此一举了。

# 地图高度固定为700，后期再生成几种
map_height = map_top

# 相机每次向上走多少距离
camera_y_split = (map_upper_right_y-map_bottom_left_y)/y_split



# 循环生成路径点
# 当相机的x轴与y轴大于或等于地图坐标时跳出循环
# 但由于x轴本质上不进行循环，因此下面的and还是只是判断相机的y轴。

animations_elements = [camera_time,{"label": "%s"%(camera_id),"r1": rotation_angle,"r2": camera_ground_angle,"r3": r3_ground,"x": camera_x,"y": camera_y,"z": map_height}]

# 终点坐标：
if (y_split & 1) == 0:
    # 如果y轴切割数量为偶数
    end_x = map_upper_right_x
    end_y = map_upper_right_y
else:
    # 如果y轴切割数量为基数
    end_x = map_bottom_left_x
    end_y = map_upper_right_y

print ("终点的坐标是:" + str(end_x) + "," + str(end_y))
# 创建/清空文件内容
# 不能用json这个库，json这个库需要将整个json读入内存才能对其进行操作
with open ("output/RA3CameraBridge.dll.camera_config.txt","w+",encoding="utf-8") as camera_config:
    pass

# 写入文件开头，以构成json
with open ("output/RA3CameraBridge.dll.camera_config.txt","a+",encoding="utf-8") as camera_config:
    camera_config.write('''{
    "cameraControls": [
        {
            "animations": [
                ''')

# 循环结构如下所示
#   循环生成rotation_angle的9种情况:-180、-135、-90、45、0、45、90、135、180
#       循环生成camera_ground_angle为90与45两种情况
#           按顺序循环生成符合要求的x,y轴的需求,并计算时间


# 循环生成camera_ground_angle为90与45两种情况
# 切换角度需要预留一下时间进行切换
for camera_ground_angle in [r2_45,r2_90]:
    # 循环生成rotation_angle的9种情况:-180、-135、-90、45、0、45、90、135、180
    for rotation_angle in [operator.neg(r1_180),operator.neg(r1_135),operator.neg(r1_90),operator.neg(r1_45),r1_0,r1_45,r1_90,r1_135,r1_180]:
        # 用while开始循环生成路径,当相机的坐标都等于最大坐标时才跳出循环。
        # 其实只需要判断camera_y < end_y即可
        # 每轮都从左下角原点重新开始
        # 在原点进行切换视角，时间1秒
        camera_id = 1
        camera_x = map_bottom_left_x
        camera_y = map_bottom_left_y
        camera_time = camera_time+1
        animations_elements = [camera_time,{"label": "%s"%(camera_id),"r1": rotation_angle,"r2": camera_ground_angle,"r3": r3_ground,"x": camera_x,"y": camera_y,"z": map_height}]
        # 将路径写入文件
        with open ("output/RA3CameraBridge.dll.camera_config.txt","a+",encoding="utf-8") as camera_config:
            json.dump(animations_elements,camera_config,indent=4)
            camera_config.write(",\n")
        while True:
            if (camera_x == map_bottom_left_x) :
                # 此时相机在最左侧
                if (camera_id & 1) == 0:
                    # 当camera_id为偶数时，x轴不变，y轴数值增加
                    camera_x = camera_x
                    camera_y = camera_y+y_add
                    camera_id = camera_id + 1
                    camera_time = camera_time+y_add_time
                else:
                    # 当camera_id为奇数时，x轴数值增加
                    camera_x = camera_x+x_add
                    camera_y = camera_y
                    camera_id = camera_id + 1
                    camera_time = camera_time+x_add_time
            else:
                # 此时相机在最右侧
                if (camera_id & 1) == 0:
                    # 当camera_id为偶数时，x轴不变，y轴数值增加
                    camera_x = camera_x
                    camera_y = camera_y+y_add
                    camera_id = camera_id + 1
                    camera_time = camera_time+y_add_time
                else:
                    # 当camera_id为奇数时，x轴数值减少
                    camera_x = camera_x-x_add
                    camera_y = camera_y
                    camera_id = camera_id + 1
                    camera_time = camera_time+x_add_time

            if camera_y > end_y:
                # 当y轴大于终点y轴时,强制其为终点y轴,时间不用重新计算,最后一行不用拍摄,毕竟可以算作上一个点到达终点了
                camera_y = end_y
                if camera_x == end_x and camera_y == end_y:
                    # 到达终点后,进行回归
                    camera_id = 1
                    camera_x = map_bottom_left_x
                    camera_y = map_bottom_left_y
                    camera_time = camera_time+int(int((math.pow(int(end_x-map_bottom_left_x),2)+math.pow(int(end_y-map_bottom_left_y),2)) ** 0.5)/camera_speed)
                    animations_elements = [camera_time,{"label": "%s"%(camera_id),"r1": rotation_angle,"r2": camera_ground_angle,"r3": r3_ground,"x": camera_x,"y": camera_y,"z": map_height}]
                    print ("生成完成"+"视角:"+str(rotation_angle)+","+"俯仰角:"+str(camera_ground_angle))
                    # 将路径写入文件
                    with open ("output/RA3CameraBridge.dll.camera_config.txt","a+",encoding="utf-8") as camera_config:
                        json.dump(animations_elements,camera_config,indent=4)
                        camera_config.write(",\n")
                    break


            animations_elements = [camera_time,{"label": "%s"%(camera_id),"r1": rotation_angle,"r2": camera_ground_angle,"r3": r3_ground,"x": camera_x,"y": camera_y,"z": map_height}]
            # 将路径写入文件
            with open ("output/RA3CameraBridge.dll.camera_config.txt","a+",encoding="utf-8") as camera_config:
                json.dump(animations_elements,camera_config,indent=4)
                camera_config.write(",\n")
            



# 使用shell脚本对文件进行处理,删除最后一个逗号
os.system("powershell sed -i '$s/,$//' output/RA3CameraBridge.dll.camera_config.txt")

# 当shell命令执行完成后才执行下面的命令理论上来说应该上多线程进程锁之类的,但先sleep吧
sleep(10)

# 写入文件末尾，以构成json
with open ("output/RA3CameraBridge.dll.camera_config.txt","a+",encoding="utf-8") as camera_config:
    camera_config.write(
'''            ],
            "description": "",
            "timedEvents": []
        }
    ],
    "hotkeyAnimation": "E",
    "hotkeyDisplay": "Q",
    "hotkeyPause": "W"
}''')