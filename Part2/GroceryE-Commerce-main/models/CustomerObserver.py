from Notification import Notification

class CustomerObserver(Observer): #NEED CHECKING 
    def __init__(self, full_name, email): 
        self.full_name = full_name 
        self.email = email 
        self.tracking_details = None 

    def update_notification(self, notification): 
        self.tracking_details = notification.message 
        print("Notification received: " + notification.message)
        print("Tracking details: " + self.tracking_details)

    def view_tracking_details(self, tracking_details): 
        self.tracking_details = tracking_details 
        print("Tracking details updated: " + tracking_details)
