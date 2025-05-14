import csv
import time
import numpy as np
import math
        
class Building:
    def __init__(self,name,file):
        self.name = name
        self.flex = []
        self.load = []
        self.time = []
        self.loaddata(file)

    def __str__(self):
        return(self.name)
    
    def sort_load(self):
        load = self.load
        load.sort(reverse=True)
        return(load)
    
    def loaddata(self,file1):
        with open(file1, mode = 'r') as file:
            csvFile = csv.reader(file)
            line_nr = 0
            data = []
            time = []
            for line in csvFile:
                if line_nr == 1:
                    name = line[0].split(';')[1:]
                    #print(name)
                if line_nr > 1:
                    data.append(line[0].split(';')[1:])
                    time.append(line[0].split(';')[0])
                line_nr += 1
        for i in range(len(name)):
            if self.name == name[i]:
                #print(name[i])
                list_load = []
                list_time = []
                for j in range(len(data)):
                    list_load.append(float(data[j][i]))
                    list_time.append(time[j])
                self.load = list_load
                self.time = list_time

    def add_flex(self,capasity,duration,rest,priorety,flex):
        self.flex.append(flexres(capasity,duration,rest,priorety,flex))

class flexres:
    def __init__(self,capasity,duration,rest,priorety,flex = bool):
        self.capasity = capasity
        self.capasityP = 100
        self.duration = duration
        self.priorety = priorety
        self.flex = flex
        self.rest = rest
        self.restS = False
        self.status = False
        self.statusS = 0

    def __repr__(self):
        return(f"CapasityP:{self.capasityP}")
        #return(f"Priorety:{self.priorety}, Capasity:{self.capasity}")
    
    def __eq__(self, other):
        return(not(self.capasity < other.capasity))
    def __lt__(self, other):
        return(self.priorety < other.priorety)

    def use(self,timestep,mengde = 0 ,check = False):
        if self.flex == False:
            shed = self.capasity*timestep/3600
            if not check: 
                self.capasityP -= timestep/self.duration*100
                self.statusS = 1
            if self.capasityP <= 0:
                self.restS = True
                self.statusS = 2
        return(shed)
    
    def resting(self,timestep,check = False):
        rest = 100 - self.capasityP
        if rest > timestep/self.rest*100:
            load = self.capasity*self.duration/self.rest*timestep/3600
            if check == False:
                self.capasityP += timestep/self.rest*100
        else:
            load = self.capasity*self.duration/3600*rest/100
            if check == False:
                self.capasityP += rest
        if self.capasityP == 100:
            self.restS = False
            self.statusS = 0
        return(load)
     
def Sum_buliding_load(Buildings, Sort = False, Dict = False):
    load_list = None
    for Building in Buildings:
        if load_list == None:
            load_list = Building.load
        else:
            load_list = list(np.add(load_list, Building.load))
    if Sort:
        load_list.sort()
        load_list = load_list[::-1]
    if Dict:
        DictH = {}
        for i in range(len(load_list)):
            DictH[i+1] = load_list[i]
        return(DictH)
    return(load_list)

def Peak_Dur(Buildings, threshold,timestep):
    counter = 0
    counter_mem = 0
    prev = 0
    load_list = Sum_buliding_load(Buildings)
    for load in load_list:
        if load > threshold:
            counter += 1
            prev = load
        elif prev > threshold and counter > counter_mem:
            counter_mem = counter
            counter = 0
    return(counter_mem*timestep)

def Save_Csv(filename,load):
    with open(filename,'w') as file:
         for line in load:
            file.write(f"{str(line)}\n")

def load_Csv(fil):
    list = []
    with open(fil, 'r') as file:
        for line in file:
            list.append(float(line))
    return list

def decode_int(int , system, fill = None):
    list = []
    while True:
        if int >= system:
            rest =int - system*math.floor(int/system)
            list.append(rest)
            int = math.floor(int/system)
        else:
            list.append(int)
            if fill and len(list) < fill:
                while len(list) < fill:
                    list.append(0)
            break
    return list

def is_closer(val1,val2,target,rev= False):
    if rev:
        if val2 == None:return True
        elif val1 - target > 0 and val2 - target < 0:return False
        else:
            if abs(val1 - target) < abs(val2 - target):return True
            else: return False
    else:
        if val2 == None:return True
        elif val1 - target < 0 and val2 -target > 0:return False
        else:
            if abs(val1 - target) < abs(val2 - target):return True
            else: return False
        
    
if __name__ == "__main__":
    LoadSource = "LoadProfile_20IPs_2016.csv"

    Building1 = Building("LG 1",LoadSource)

    print(Building1.load)