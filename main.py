''' 
Proponowana architketura :to 1 producent i wiele watków. Wydaje się 
że nie ma potrzeby uruchamiać wielu wątków prodcuenta gdy źródło produkuje
wolniej niż przetwarza producent. Tak rozumiem zapis o tym, że producent pobiera 
dane z źródła co 50ms.  

Ponieważ Python przetwarza wątki współbieżnie, ale nie równolegle to 
pomiar czasu nie pokaże zysku na czasie z tytułu uruchomienia wielu wątków 
konsumenta.Nie zobaczymy go również gdy czas przetwarzania producenta 
i konsumenta będzie krótszy niż tempo produkcji nowych obrazów przez źródło


'''

import threading
import queue
import source
import time
import cv2 
import os 

end_of_cons=threading.Event()

def make_dir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

def write_images(path,queue):
    make_dir(path)
    for name in range(queue.qsize()):
        image=queue.get()
        cv2.imwrite(path+str(name)+'.png',image)

def transform_image(image):
    image = cv2.resize(image, (int(image.shape[0]/2),int(image.shape[1]/2)), interpolation = cv2.INTER_LINEAR)
    image = cv2.medianBlur(image,5)
    return image

def producer(source, queue_producer,images_count):
    while not end_of_cons.is_set():
        queue_producer.put(source.get_data())
        images_count-=1
        time.sleep(0.05)
    
def consumer(queue_producer,queue_consumer,images_count):
    
    while not end_of_cons.is_set():
            try:   
             image=queue_producer.get_nowait()
            except: pass
            else :
                image=transform_image(image)
                try :
                    queue_consumer.put_nowait(image)
                except:
                    end_of_cons.set()

def main():

    path = './processed/'
    rows = 786
    cols = 1024
    channels = 3

    images_count = 100
    consumer_threads_count = 3

    source_of_image=source.Source((rows,cols,channels))

    queue_producer=queue.Queue(maxsize=images_count)
    queue_consumer=queue.Queue(maxsize=images_count)


    prod = threading.Thread(target=producer,args=(source_of_image,
                                                    queue_producer,
                                                    images_count))

    cons =[ threading.Thread(target=consumer,args=(queue_producer,
                                                    queue_consumer,
                                                    images_count,))
            for _ in range(consumer_threads_count) ]

    t=time.time()
    
    prod.start()
    for c in cons: c.start()

    prod.join()
    for c in cons: c.join()

    write_images(path,queue_consumer)

    print('Czas dla',consumer_threads_count,'watkow', time.time()-t)
    

if __name__=='__main__':main()


