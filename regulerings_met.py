from Funktioner import *
import numpy as np
import time 
import math
import matplotlib.pyplot as plt

def Prioritets_reg(Buildings,timestep,threshold,slic):
    load_list = []
    flex_used = []
    flexres_list = []
    tload = Sum_buliding_load(Buildings)
    tot_load = tload[slic]
    print(len(tot_load))
    for Building in Buildings:
        flexres_list.extend(Building.flex)
    flexres_list.sort()
    for load in tot_load:
        load_after = load
        for flexres in flexres_list:
            if flexres.restS == True: #Check if flexres is resting
                load_after += flexres.resting(timestep)
                flexres.status = True
        for flexres in flexres_list:
            if flexres.status != True:
                if load_after > threshold: #Check if flexres is needed
                    load_after -= flexres.use(timestep)
                elif load_after + flexres.resting(timestep,check = True) <= threshold and flexres.capasityP < 100: #Check if extra capasity for rest
                    load_after += flexres.resting(timestep)
            else:
                flexres.status = False
        flex_used.append(load - load_after)
        load_list.append(load_after)
    return(load_list, flex_used)

def Pri_reg_Stat(Buildings, timestep, threshold,slic):
    load_list = []
    flex_used = []
    flexres_list = []
    tot_load = Sum_buliding_load(Buildings)
    tot_load = tot_load[slic]
    for Building in Buildings:
        flexres_list.extend(Building.flex)
    flexres_list.sort()
    for load in tot_load:
        load_after = load
        for flexres in flexres_list:
            if flexres.statusS == 1:
                load_after -= flexres.use(timestep)
                flexres.status = True
            elif flexres.statusS == 2:
                load_after += flexres.resting(timestep)
                flexres.status = True
        for flexres in flexres_list:
            if flexres.status != True and flexres.statusS == 0:
                if load_after > threshold: #Check if flexres is needed
                    load_after -= flexres.use(timestep)
            else:
                flexres.status = False
        flex_used.append(load - load_after)
        load_list.append(load_after)
    return(load_list, flex_used)

def Opti_reg_Stat(Buildings,timestep,threshold,slic):
    load_list = []
    flex_used = []
    flexres_list = []
    tot_load = Sum_buliding_load(Buildings)
    tot_load = tot_load[slic]
    for Building in Buildings:
        flexres_list.extend(Building.flex)
    for load in tot_load:
        load_after = load
        flexlist = []
        for flexres in flexres_list:
            if flexres.statusS == 1:
                load_after -= flexres.use(timestep)
            elif flexres.statusS == 2:
                load_after +=  flexres.resting(timestep)
            else:
                flexlist.append(flexres)
        if load_after > threshold:
            value = load_after-threshold
            low_flex_load = None
            low_flex_list = []
            for i in range(1,2**len(flexlist)):
                flex_load = 0
                list = decode_int(i,2,len(flexlist))
                for x in range(len(list)):
                    if list[x]:
                        flex_load += flexlist[x].use(timestep,check = True)
                if is_closer(flex_load,low_flex_load,value):
                    low_flex_load = flex_load
                    low_flex_list = list.copy()
            #print(f"Overstigning:{value},Flex brukt:{low_flex_load}",end='')
            for i in range(len(flexlist)):
                if low_flex_list[i]:
                    load_after -= flexlist[i].use(timestep)
        flex_used.append(load - load_after)
        load_list.append(load_after)
    return(load_list, flex_used)

def Opti_reg(Buildings,timestep,threshold,slic):
    load_list = []
    flex_used = []
    flexres_list = []
    tot_load = Sum_buliding_load(Buildings)
    tot_load = tot_load[slic]
    for Building in Buildings:
        flexres_list.extend(Building.flex)
    for load in tot_load:
        load_after = load
        flexlist = []
        Used = False
        for flexres in flexres_list:
            if flexres.restS == True: #Check if flexres is resting
                load_after += flexres.resting(timestep)
            else:
                flexlist.append(flexres)
        if load_after > threshold:
            value = load_after-threshold
            low_flex_load = None
            low_flex_list = []
            rem_list = []
            for i in range(1,2**len(flexlist)):
                flex_load = 0
                list = decode_int(i,2,len(flexlist))
                for x in range(len(list)):
                    if list[x]:
                        flex_load += flexlist[x].use(timestep,check = True)
                if is_closer(flex_load,low_flex_load,value):
                    low_flex_load = flex_load
                    low_flex_list = list.copy()
            #print(f"Overstigning:{value},Flex brukt:{low_flex_load}",end='')
            Used = True
            for i in range(len(flexlist)):
                if low_flex_list[i]:
                    load_after -= flexlist[i].use(timestep)
                    rem_list.append(i)
            flexlist = np.delete(flexlist,rem_list)
        low_rest_load = None       
        low_rest_list = []
        value = threshold - load_after
        if value > 0:
            for i in range(0,2**len(flexlist)):
                flex_rest = 0
                list = decode_int(i,2,len(flexlist))
                for x in range(len(list)):
                    if list[x]:
                        flex_rest += flexlist[x].resting(timestep,check = True)
                if is_closer(flex_rest,low_rest_load,value,True):
                    low_rest_load = flex_rest
                    low_rest_list = list.copy()
            for i in range(len(flexlist)):
                if low_rest_list[i]:
                    load_after += flexlist[i].resting(timestep)
        if low_rest_load != 0 and low_rest_load != None:
            #print(f" Verdi:{value},Rest brukt:{low_rest_load}")
            pass
        elif Used:
            #print("")
            pass
        flex_used.append(load - load_after)
        load_list.append(load_after)
    return(load_list,flex_used)

def listReg(Buildings,timestep):
    energy_price = [37.23,30.69,30.66,27.96,35.69,44.92,72.4,79.77,82.65,71.69,54.29,27.58,27.75,35.8,34.33,32.1,60.7,78.14,82.05,82.17,81.7,81.32,79.27,76.14]
    energy_price_s = np.repeat(energy_price, int(3600 / timestep))
    list = load_flex_use_from_file()
    liste = np.zeros(96)
    liste2 = np.zeros(96)
    liste3 = np.zeros(96)
    day = [11,8,7,9]
    flexres_list = []
    plt.figure(figsize=(10, 10))
    for Building in Buildings:
        flexres_list.extend(Building.flex)
    for i in range(len(Buildings)):
        tot_load = Buildings[i].load[(day[i]-1)*96:day[i]*96]
        load_list = []
        flex_used = []
        index = 0
        for load in tot_load:
            used = set()
            load_after = load
            for flexres in flexres_list:
                if flexres.statusS == 1:
                    load_after -= flexres.use(timestep)
                elif flexres.statusS == 2:
                    load_after +=  flexres.resting(timestep)
            for x in range(3):
                if list[1+3*i+x][index-1] == 1 and flexres_list[3*i+x].statusS == 0:
                    #print(f"Flexres status:{flexres_list[3*i+x].statusS}, {1+3*i+x} at time {index}")
                    print(f"Used flexres {1+3*i+x} at time {index}")
                    load_after -= flexres_list[3*i+x].use(timestep)
                    #print(f"Flexres status:{flexres_list[3*i+x].statusS}, {1+3*i+x} at time {index},After")
            flex_used.append(load - load_after)
            load_list.append(load_after)
            index += 1
        print(f"Max før:{max(tot_load)}, max etter:{max(load_list)}, sum før:{sum(tot_load)}, sum etter:{sum(load_list)}, Pris: {sum(np.multiply(load_list,energy_price_s))}")
        liste = np.add(liste,load_list)
        liste2 = np.add(liste2,flex_used)
        liste3 = np.add(liste3,tot_load)
        plt.subplot(5,2,i*2+1)
        plt.plot(tot_load, label="Original Load")
        plt.plot(load_list, label="Net Load After Flex")
        plt.plot(flex_used, label="Flex Used")
        plt.title(f"{Buildings[i].name} Lastkurve")
        plt.xlabel("Tid(15 min. intervaller)")
        plt.ylabel("kW")
        plt.grid(True)
        plt.tight_layout()
        plt.subplot(5,2,i*2+2)
        plt.title("Varighetskurve")
        tot_load.sort()
        tot_load = tot_load[::-1]
        load_list.sort()
        load_list = load_list[::-1]
        plt.plot(tot_load, label="Original Load")
        plt.plot(load_list, label="Net Load After Flex")
        plt.xlabel("Tid(15 min. intervaller)")
        plt.ylabel("kW")
        plt.grid(True)
        plt.tight_layout()
    plt.subplot(5,2,4*2+1)
    plt.plot(liste3, label="Original Load")
    plt.plot(liste, label="Net Load After Flex")
    plt.plot(liste2, label="Flex Used")
    plt.title("Total Lastkurve")
    plt.xlabel("Tid(15 min. intervaller)")
    plt.ylabel("kW")
    plt.grid(True)
    plt.tight_layout()
    plt.legend(fontsize='small', loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    plt.subplot(5,2,4*2+2)
    liste3.sort()
    liste3 = liste3[::-1]
    liste.sort()
    liste = liste[::-1]
    plt.plot(liste3, label="Original Load")
    plt.plot(liste, label="Net Load After Flex")
    plt.title("Varighetskurve")
    plt.xlabel("Tid(15 min. intervaller)")
    plt.ylabel("kW")
    plt.grid(True)
    plt.tight_layout()
    plt.legend(fontsize='small', loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    print(f"Max før:{max(liste3)}, Max etter:{max(liste)},Gjennomsnitt før:{np.average(liste3)},Gjennomsnitt etter:{np.average(liste)}, Avik:{sum(liste3)-sum(liste)} Sum før:{sum(liste3)}, Sum etter:{sum(liste)}")
    plt.show()
    return(liste3, liste, liste2)

def load_flex_use_from_file(filename="flex_use_matrix.txt"):
    flex_use = {}
    with open(filename, "r") as file:
        lines = file.readlines()
        current_resource = None
        for line in lines:
            line = line.strip()
            if line.startswith("Resource"):
                # Extract the resource ID
                current_resource = int(line.split()[1].strip(":"))
                flex_use[current_resource] = []
            elif current_resource is not None:
                # Add the values to the current resource
                flex_use[current_resource].extend(map(float, line.split()))
    
    # Convert lists to numpy arrays for easier manipulation
    for r in flex_use:
        flex_use[r] = np.array(flex_use[r])
    
    return flex_use

