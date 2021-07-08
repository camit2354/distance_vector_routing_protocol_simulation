import threading
import os
import time
import sys

shared_queue = []
events_for_routers_from_nbrs = {}


def is_dvr_of_nbrs_rcvd_from_all(nbrs):
    status = True
    for i in nbrs:
        if nbrs[i] == 0:
            status = False
    return status


def router_task(mat, lock, router_names):

    myRname = threading.current_thread().name
    dvr = {}
    nbrs = []
    fwt_table = []
    mark_nbrs = {}
    nbrs_dvr = {}
    mark_updtd = {}

    ##################### router initialization at  start

    for i in router_names:
        dvr[i] = mat[myRname][i]
        mark_updtd[i] = "-"
        if dvr[i] > 0 and dvr[i] < 1000:
            nbrs.append(i)

    ##############################################33

    for itr in range(5):

        # Forward  self  distance  vector  to neibhours
        for i in nbrs:
            lock.acquire()
            fwt_table = [myRname, i, dvr]
            shared_queue.append(fwt_table)
            mark_nbrs[i] = 0
            lock.release()

        # Wait  till  all  neibhours  request  has  reached  to  u
        while is_dvr_of_nbrs_rcvd_from_all(mark_nbrs) == False:
            lock.acquire()

            if len(shared_queue) > 0:
                if shared_queue[0][1] == myRname:
                    mark_nbrs[shared_queue[0][0]] = 1
                    nbrs_dvr[shared_queue[0][0]] = shared_queue[0][2]
                    shared_queue.pop(0)
                    lock.release()
                    if len(shared_queue) > 0:
                        events_for_routers_from_nbrs[shared_queue[0][1]].set()

                else:
                    events_for_routers_from_nbrs[shared_queue[0][1]].set()
                    lock.release()
                    events_for_routers_from_nbrs[myRname].wait()

        # print  router  state
        lock.acquire()

        print(" ITERATION : " + str(itr) + "    ^   ROUTER-NAME  : " + myRname)
        print(" MY  DISTANCE  VECTOR ")
        for i in dvr:
            print(mark_updtd[i] + "   " + myRname + " - > " + i + " : " + str(dvr[i]))

        print(" *******************************  \n")

        # updation  code dist vector : bellman  ford

        for i in dvr:
            mark_updtd[i] = "-"

        for i in dvr:
            for j in nbrs:
                if dvr[i] > mat[myRname][j] + nbrs_dvr[j][i]:
                    dvr[i] = mat[myRname][j] + nbrs_dvr[j][i]
                    mark_updtd[i] = "*"

        lock.release()

        time.sleep(4)


if __name__ == "__main__":
    config_file = sys.argv[1]
    with open(config_file, "r") as f:
        input_mat = [line.split() for line in f]

        no_of_routers = int(input_mat[0][0])
        router_names = input_mat[1]

        lock = threading.Lock()
        t = []

        mat = {}
        for i in router_names:
            mat[i] = {}
            for j in router_names:
                mat[i][j] = 1000
                if i == j:
                    mat[i][j] = 0

        for i in range(2, len(input_mat)):
            mat[input_mat[i][0]][input_mat[i][1]] = int(input_mat[i][2])
            mat[input_mat[i][1]][input_mat[i][0]] = int(input_mat[i][2])

        for i in range(no_of_routers):
            t.append(
                threading.Thread(
                    target=router_task,
                    args=(mat, lock, router_names),
                    name=router_names[i],
                )
            )
            events_for_routers_from_nbrs[router_names[i]] = threading.Event()

        for i in range(no_of_routers):
            t[i].start()

        for i in range(no_of_routers):
            t[i].join()

        print("for  simplicity  i  have  iterated for  5  times ")
