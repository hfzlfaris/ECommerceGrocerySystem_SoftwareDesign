class PaymentBuilder(ABC): 
    @abstractmethod
    def productPrice(self): 
        pass 
    
    @abstractmethod
    def addedTax(self): 
        pass 

    @abstractmethod
    def shippingCost(self): 
        pass
    
    @abstractmethod
    def totalPrice(self): 
        pass 

    