from Notification import Notification 

class Subject: 
    def __init__(self):
        self._observers = []
        self._state = None

    def add_observer(self, observer): 
        self._observers.append(observer)
    
    def remove_observer(self, observer): 
        self._observers.remove(observer)

    def notify_observers(self): 
        for observer in self._observers: 
            observer.update_notification(notification)




