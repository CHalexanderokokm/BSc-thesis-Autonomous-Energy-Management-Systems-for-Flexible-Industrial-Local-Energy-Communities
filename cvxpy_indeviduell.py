import numpy as np
import cvxpy as cp
import matplotlib.pyplot as plt
from Funktioner import *

LoadSource = "LoadProfile_20IPs_2016.csv"
timestep = 900
day = [11,8,7,9]
energy_price = [37.23,30.69,30.66,27.96,35.69,44.92,72.4,79.77,82.65,71.69,54.29,27.58,27.75,35.8,34.33,32.1,60.7,78.14,82.05,82.17,81.7,81.32,79.27,76.14]
energy_price_s = np.repeat(energy_price, int(3600 / timestep))
pros = [54.7,9.9,23.8,11.6]
liste_load = np.zeros(96)
liste_flex = np.zeros(96)
liste_net = np.zeros(96)
over = []
plt.figure(figsize=(10, 10))

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
thresh = 500
for i in range(len(Buildings)):
    liste_load = np.add(liste_load,Buildings[i].load[(day[i]-1)*96:day[i]*96])
for load in liste_load:
    if load > thresh:
        over.append(load - thresh)
        print(load - thresh)
    else:
        over.append(0)
for i in range(len(Buildings)):
    load = Buildings[i].load[(day[i]-1)*96:day[i]*96]
    plot = 1 +2*i

    T = len(load)
# Flex resources
    resources = {}
    for flexr in Buildings[i].flex:
        flexr.use(timestep)
        resources[len(resources)+1] = {"capacity": flexr.use(timestep, check = True),"duration":int(flexr.duration/timestep),"rest":int(flexr.rest/timestep),"rest_load":flexr.resting(timestep,check = True)}

    print(resources)
    R = list(resources.keys())

    # Variables: flex_use[r, t] → binary: start flex block
    flex_use = {
        r: cp.Variable(T, boolean=True)
        for r in R
    }

    # Variables: flex[t] = total flexible capacity at time t
    flex = cp.Variable(T)
    # Variables: max_load = peak load
    max_load = cp.Variable()

    over_t = cp.Variable(T)

    constraints = []

    hold = None
    # 0. Flex must not exceed actual load
    for t in range(T):
        constraints.append(flex[t] <= load[t])

    # 1. Peak load constraint
    for t in range(T):
        constraints.append(max_load >= load[t] - flex[t])

    # 2. Compute flex at time t
    for t in range(T):
        expr = 0
        for r in R:
            cap = resources[r]["capacity"]
            dur = resources[r]["duration"]
            rest = resources[r]["rest"]
            rest_load = resources[r]["rest_load"]

            for tau in range(T):
                if tau + dur + rest <= T:
                    if tau <= t < tau + dur:
                        expr += cap * flex_use[r][tau]
                    elif tau + dur <= t < tau + dur + rest:
                        expr -= rest_load * flex_use[r][tau]
        constraints.append(flex[t] == expr)

    # 3. Enforce activation/rest non-overlap
    for r in R:
        dur = resources[r]["duration"]
        rest = resources[r]["rest"]
        window = dur + rest
        for t in range(T - window + 1):
            constraints.append(
                cp.sum(flex_use[r][t:t + window]) <= 1
            )

    for t in range(T):
        if liste_load[t] > thresh and over[t]*pros[i]/100 < load[t]:
            print(f"flex needed:{over[t]*pros[i]/100}, load:{load[t]}, time:{t}")
            constraints.append(flex[t] >= over[t]*pros[i]/100)
        elif liste_load[t] > thresh:
            constraints.append(flex[t] >= 0)
            #constraints.append(flex[t] >= 0)
    # Objective: minimize peak load
    #objective = cp.Minimize(cp.sum(cp.abs(flex)))
    objective = cp.Minimize(max_load)
    #objective = cp.Minimize(cp.sum(cp.multiply(energy_price_s, load - flex)))
    # Solve
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.GLPK_MI)

    # Extract results
    if prob.status == cp.OPTIMAL:
        print("✅ Optimal solution found.\n")
    else:
        print("❌ Solver failed:", prob.status)

    flex_val = flex.value
    net_load = load - flex_val
    liste_flex = np.add(liste_flex,flex_val)
    liste_net = np.add(liste_net,net_load)

    # Print schedule
    max_price = 0
    for r in R:
        times = np.where(flex_use[r].value > 0.5)[0]
        for t in times:
            dur = resources[r]['duration']
            rest = resources[r]['rest']
            print(f"Resource {r} used at t={t+1}: Active {t+1}-{t+dur}, Rest {t+dur+1}-{t+dur+rest}")
    print(f"Max before: {max(load):.2f}, max after: {max(net_load):.2f}, flex used: {sum(abs(flex_val))/2:.2f}")
    print(f"Load before: {sum(load):.2f}, load after: {sum(net_load):.2f}")
    print(f"Energy price before: {sum(load[t]*energy_price_s[t] for t in range(T))}, "
          f"energy price after: {sum(net_load[t]*energy_price_s[t] for t in range(T))}")

    # Plotting
    plt.subplot(5,2,plot)
    plt.plot(range(1, T + 1), load, label="Original Load")
    plt.plot(range(1, T + 1), net_load, label="Net Load After Flex")
    plt.plot(range(1, T + 1), flex_val, label="Flex Used")
    plt.plot(range(1, T + 1), energy_price_s, label="Energy Price")
    plt.title(Buildings[i].name)
    plt.xlabel("Hour")
    plt.ylabel("kW") # Adjust legend size
    plt.grid(True)
    plt.tight_layout()
    plt.subplot(5,2,plot+1)
    load.sort()
    load = load[::-1]
    net_load.sort()
    net_load = net_load[::-1]
    plt.plot(range(1, T + 1), load, label="Original Load")
    plt.plot(range(1, T + 1), net_load, label="Net Load After Flex")
    plt.ylabel("kW")  # Adjust legend size
    plt.grid(True)
    plt.tight_layout()
print(f"Max before: {max(liste_load):.2f}, max after: {max(liste_net):.2f}")
print(f"Load before: {sum(liste_load):.2f}, load after: {sum(liste_net):.2f}")
print(f"Energy price before: {sum(liste_load[t]*energy_price_s[t] for t in range(T))}, "
          f"energy price after: {sum(liste_net[t]*energy_price_s[t] for t in range(T))}")
plt.subplot(5,2,plot+2)
plt.title("Total")
plt.plot(range(1, T + 1), liste_load, label="Original Load")
plt.plot(range(1, T + 1), liste_net, label="Net Load After Flex")
plt.plot(range(1, T + 1), liste_flex, label="Flex Used")
plt.plot(range(1, T + 1), energy_price_s, label="Energy Price")
plt.xlabel("Hour")
plt.ylabel("kW")
plt.legend(fontsize='small', loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
plt.grid(True)
plt.tight_layout()
plt.subplot(5,2,plot+3)
liste_load.sort()
liste_load = liste_load[::-1]
liste_net.sort()
liste_net = liste_net[::-1]
plt.plot(range(1, T + 1), liste_load, label="Original Load")
plt.plot(range(1, T + 1), liste_net, label="Net Load After Flex")
plt.ylabel("kW")
plt.legend(fontsize='small', loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)  # Adjust legend size
plt.grid(True)
plt.tight_layout()

# Adjust vertical spacing between subplots
#plt.subplots_adjust(hspace=0.5)  # Adjust hspace as needed

#plt.rcParams['interactive'] == True

plt.show()
