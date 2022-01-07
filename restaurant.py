
from random import randint
import simpy

# Global Variables
hours = 0
days = []
months = 0
total_profit = []
total_profit_count = 0  # used as index for total profit list
customer_count = 0  # The number of customers in all months
customer_arrival = []
cusPerDay1=[]# this is a list of customers numbers over all the days
g = [0, 0, 0, 0, 0]  # this is a list for games load chart
wait1=[]
wait2=[]
wait3=[]
w1 = 0
w2= 0
w3=0

# items
Items = {
    0: {'name': 'Item1', 'price': 2, 'time_to_finish': randint(1, 10), 'gain': 2 - (2 * 30 / 100)},
    1: {'name': 'Item2', 'price': 4, 'time_to_finish': randint(10, 15), 'gain': 4 - (4 * 30 / 100)},
    2: {'name': 'Item3', 'price': 5, 'time_to_finish': randint(10, 15), 'gain': 5 - (5 * 30 / 100)},
    3: {'name': 'Item4', 'price': 8, 'time_to_finish': randint(20, 30), 'gain': 8 - (8 * 30 / 100)},
    4: {'name': 'Item5', 'price': 10, 'time_to_finish': randint(20, 30), 'gain': 10 - (10 * 30 / 100)},
}
# Monthly costs
Restaurant_place_installment = 2200
Employees_monthly_salaries = (1200 * 3) + (800 * 2)
Tax = .14

# This function generates the interarrival time customers
def get_Customers_next_interarrival():
    return randint(0, 90)
# This function generates a random number between 0 and 100, to help us in any percentage
def get_others_next_interarrival():
    return randint(0, 100)  # 0 and 100 are included
# This function determine the type of custmer according to the random number
def get_Cust_types():
    randN = get_others_next_interarrival()
    if randN <= 75:
        return "normal"
    else:
        return "vip"
# This function returns number of items the customer order
def get_number_of_items():
    randN = get_others_next_interarrival()
    if randN <= 25:
        return 1
    elif randN <= 65:
        return 2
    elif randN <= 90:
        return 3
    else:
        return 4
# This function  generates a random number of customer
def get_number_of_cust():
    randN = get_Customers_next_interarrival()
    if randN <= 30:
        return 1
    elif randN <= 70:
        return 2
    elif randN <= 90:
        return 3
    else:
        return 4
# This function  return items
def get_item():
    global Items
    randN = get_others_next_interarrival()
    if randN <= 10:
        g[0] += 1
        return Items[0]
    elif randN <= 30:
        g[1] += 1
        return Items[1]
    elif randN <= 60:
        g[2] += 1
        return Items[2]
    elif randN <= 90:
        g[3] += 1
        return Items[3]
    else:
        g[4] += 1
        return Items[4]
# This function returns the priority number
def get_priority(cust):
    if cust.cus_type == "normal":
        return 0  # 0 for lower priority
    else:
        return -1  # -1 for higher priority
class customer:
    def __init__(self, env):
        self.env = env
        self.number=get_number_of_cust()
        #print(self.number)
        self.interarrival = get_Customers_next_interarrival()
        self.number_of_items = get_number_of_items()
        self.cus_type = get_Cust_types()
        self.items = {}
        #self.time=0
        #self.time_take=randint(1,4)
        for j in range(self.number):
            for i in range(self.number_of_items):
                self.items[i] = get_item()
        #for i in self.items:
            #self.time+=self.items[i]['time_to_finish']
        #self.time+=self.time_take
        # print(self.items[i].name )

def waiter(cust,waiterr,cookers_qq,env):
    global w1  ,w2 ,w3
    #prio=get_priority(cust)
    with waiterr.request() as req:
        yield req
        time_take_order = randint(1, 4)

        if waiterr.count == 1:
            w1+=cust.number
        elif waiterr.count == 2:
            w2 += cust.number
        elif waiterr.count == 3:
            w3 += cust.number
        yield env.timeout(time_take_order)
        cooker(env, cust.items, cookers_qq, prio=get_priority(cust))
def cooker(env,items,cookers_qq,prio):
    global cooker_duration
    with cookers_qq.request(priority=prio) as req:
        yield req
        for i in items:
           cooker_duration+=items[i]['time_to_finish']
        yield env.timeout(cooker_duration)
        cooker_duration=0

cooker_duration=0

# Check the total profit at the end of each month
def monthly_check(env):
    global total_profit, Tax, Restaurant_place_installment, Employees_monthly_salaries,  total_profit_count
    
    while True:
        yield env.timeout(30 * 24 * 60)
        total_profit[total_profit_count] -= (Tax * total_profit[total_profit_count])+ Restaurant_place_installment + Employees_monthly_salaries
            
        #print(total_profit_count,total_profit)
        total_profit_count += 1
        total_profit.append(0)
        

def run(env):
    global w1,w2,w3,total_profit, months, normal, special,cusPerDay1, customer_count,  days, hours, total_profit_count,wait1,wait2,wait3
    total_profit.append(0)
    #months = int(env.now / (30 * 24 * 60))
    months +=1
    env.process(monthly_check(env))
    cookers_q = simpy.PriorityResource(env, capacity=2)
    waiterr = simpy.Resource(env, capacity=3)
    i = 0           # used as a customer name
    c = 1           # counter for days list   days=[1, 2, 3, 4, ..]
    a = 1           # we multiply this factor to 12 to check if the day is end or not .. is >=12  .. >=36 and so on ..
    cusPerDay = 0   # number of customers per day
    n=0

    while True:
        cust = customer(env)
        n = n+cust.number

        customer_count += 1
        cusPerDay += cust.number
        yield env.timeout(cust.interarrival)
        hours = env.now / 60
        if hours > 12 * a:
            # check if the day is end
            yield env.timeout(60 * 12)
            #print(w1,w2,w3)
            wait1.append(w1)
            wait2.append(w2)
            wait3.append(w3)
            days.append(c)
            customer_arrival.append(cusPerDay)
            cusPerDay1.append(w1+w2+w3)
            cusPerDay = 0
            w1=0
            w2=0
            w3=0
            #print("day %s customer per day %s" % (days[c-1],customer_arrival[c-1]))
            #print("customer_count %s" % (customer_count))
            c += 1
            a += 2
            #print(a)
        for g in range(cust.number_of_items):
            total_profit[total_profit_count] += cust.items[g]["gain"]
            #print(total_profit)
            env.process(waiter(cust, waiterr,cookers_q,env))
            #print("done")
    #print("done")
    months = int(env.now / (30 * 24 * 60))
    #print('Total profit: %s$ in %s months with total customer %s' % (sum(total_profit), months, customer_count))
    total_profit.clear()
    customer_count = 0
    total_profit_count = 0
# Called by the GUI to start the simulation
def startSim(number_sim,N):
    global number_of_simulation
    number_of_simulation = number_sim
    for i in range(number_of_simulation):
        env = simpy.Environment()
        env.process(run(env))
        env.run(until=N*30*24*60+1)



