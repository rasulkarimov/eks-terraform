from multiprocessing import Pool
import psutil
import time

def f(x):
    set_time = 1
    timeout = time.time() + 90 * float(set_time)  
    while True:
        if time.time() > timeout:
            break

def main():
    processes = psutil.cpu_count()
    print('utilizing %d cores\n' % processes)
    pool = Pool(processes)
    pool.map(f, range(processes))

if __name__ == '__main__':
    main()  