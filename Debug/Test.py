import Training as Trainer
import _thread
import threading
import time

def print_epoch(name_of_thread, delay):
    count = 0
    while count < 5:
        time.sleep(delay)
        count+=1
        print(name_of_thread, "----------",time.time())
class MyThread(threading.Thread):
    def __init__(self, name, delay):
        threading.Thread.__init__(self)
        self.name = name
        self.delay = delay


    def run(self):
        print("Start Thread", self.name)
        print_epoch(self.name,self.delay)
        print("End Thread", self.name)
        Trainer.Train()
if __name__== '__main__':
    try:
        training_thread =threading.Thread(target=MyThread, args=("Training Thread", delay))
        training_thread.start()
        training_thread.join()

    except:
        print("Program Encountered an Error")




