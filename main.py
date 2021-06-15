import simpy
import random
#   p0  p1  p2 p3...pN
# f0  f1 f2  f3.. fN...f0

def philosofer(env:simpy.Environment, name:str, left_fork:simpy.Resource, right_fork:simpy.Resource, ev:simpy.Event)\
        -> simpy.Event:
    thinking_time=21
    eating_time=5
    max_waiting_time=9

    lf:simpy.Request
    rf:simpy.Request

    while True:
        time = thinking_time+random.randint(0,10)/100
        print(f'[{env.now:4.2f}] {name} is thinking for {time}min')
        yield env.timeout(time)
        time = env.now
        with left_fork.request() as lf:
            print(f'[{env.now:4.2f}] {name} is waiting for left fork ----------')
            yield lf
            if env.now-time > max_waiting_time:
                print(f'[{env.now:4.2f}] {name} starved {env.now-time-max_waiting_time:4.2f}min ago XXXXXX')
                yield ev.fail(RuntimeError(f'{name} starved!'))
                break
            with right_fork.request() as rf:
                    print(f'[{env.now:4.2f}] {name} is waiting for right fork ----------')
                    yield rf
                    if env.now-time > max_waiting_time:
                        print(f'[{env.now:4.2f}] {name} starved {env.now-time-max_waiting_time:4.2f}min ago XXXXXX')
                        yield ev.fail(RuntimeError(f'{name} starved!'))
                        break
                    time = eating_time+random.randint(0,10)/100
                    print(f'[{env.now:4.2f}] {name} is eating for {time}min')
                    yield env.timeout(time)

#env = simpy.rt.RealtimeEnvironment(factor=0.5)
env = simpy.Environment()
num_philosophers = 5
forks = [simpy.Resource(env, capacity=1) for _ in range(num_philosophers)]

fail = env.event()

philosofers = [philosofer(env, f'p{id}', forks[id], forks[id+1], fail) for id in range(num_philosophers-1)]
philosofers.append(philosofer(env, f'p{num_philosophers-1}', forks[num_philosophers-1], forks[0], fail))

for p in philosofers:
    env.process(p)

try:
    env.run(fail)
except RuntimeError as e:
    print(str(e))