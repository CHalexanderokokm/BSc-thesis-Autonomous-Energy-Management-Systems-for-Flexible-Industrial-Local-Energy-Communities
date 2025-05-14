from Funktioner import *
from regulerings_met import *
import matplotlib.pyplot as plt
import numpy as np

LoadSource = "LoadProfile_20IPs_2016.csv"
thres = 300
timestep = 900
day = 11
sl = slice((day-1)*96,day*96)

Building1 = Building("LG 1",LoadSource)
Building1.add_flex(200,3600,7200,1,False)
Building1.add_flex(130,3600,7200,2,False)
Building1.add_flex(50,7200,14400,3,False)

Building2 = Building("LG 3",LoadSource)
Building2.add_flex(40,3600,7200,1,False)
Building2.add_flex(15,7200,7200,2,False)
Building2.add_flex(20,3600,10800,3,False)

Building3 = Building("LG 5",LoadSource)
Building3.add_flex(100,3600,7200,1,False)
Building3.add_flex(35,3600,7200,2,False)
Building3.add_flex(25,7200,14400,3,False)

Building4 = Building("LG 6",LoadSource)
Building4.add_flex(15,3600,7200,1,False)
Building4.add_flex(30,3600,7200,2,False)
Building4.add_flex(30,7200,14400,3,False)
Buildings = [Building1,Building2,Building3,Building4]
#load_list, flex_used = Prioritets_reg([Building1],timestep,thres,sl)
#load_list = DQN_reg(Building1,timestep,1,10,'0')
load_list, flex_used = Opti_reg([Building1],timestep,thres,sl)
#load_list, flex_used = Opti_reg_Stat([Building1],timestep,thres,sl)
#load_list, flex_used = Pri_reg_Stat([Building1],timestep,thres,sl)
#load_list = PyomoReg(Buildings,timestep,thres)
tot,load_list, flex_used = listReg(Buildings,timestep)

#Save_Csv(f"Optireg_thres{thres}",load_list)
tot_load = Sum_buliding_load([Building1])
tot_load = tot_load[sl]
#for building in Buildings:
#    print(f"Byggning:{building.name}, Max last:{max(building.load)}, Gjennomsnitt last:{np.average(building.load)}")
print(f"Max før:{max(tot_load)}, Max etter:{max(load_list)},Gjennomsnitt før:{np.average(tot_load)},Gjennomsnitt etter:{np.average(load_list)},Max peak varighet:{Peak_Dur(Buildings,thres,timestep)} Avik:{sum(tot_load)-sum(load_list)} Sum før:{sum(tot_load)}, Sum etter:{sum(load_list)}")
plt.figure(figsize=(10, 5))
plt.subplot(1,2,1)
plt.title("Lastkurve")
plt.plot(tot_load, label="Original Load")
plt.plot(load_list, label=f"Net Load After Flex: Threshold:{thres}")
#lt.plot(flex_used, label="Flex Used")
plt.xlabel("Tid(15 min. intervaller)")
plt.ylabel("kW")
plt.grid(True)
plt.subplot(1,2,2)
plt.title("Varighetskurve")
tot_load.sort()
tot_load = tot_load[::-1]
load_list.sort()
load_list = load_list[::-1]
plt.plot(tot_load, label="Original Load")
plt.plot(load_list, label=f"Net Load After Flex: Threshold:{thres}")
plt.xlabel("Tid(15 min. intervaller)")
plt.ylabel("kW")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


 