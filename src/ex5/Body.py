class Body:     
    def __init__(self, mass: float, heat_capacity: float,temperature : float  ):
        self.heat_capacity= heat_capacity
        self.mass= mass
        self.temperature= temperature
        if mass <= 0 or heat_capacity<=0 or temperature<0:
            raise ValueError('Error capacity ,mass and temperature must be positive')
      

    def add_heat(self,heat:float):
        dt = heat/(self.mass*self.heat_capacity)
        self.temperature = self.temperature+ dt
        return self.temperature

if __name__ == "__main__":
    body1= Body(100,0.15,200)
    print(body1.add_heat(20))
    print(body1.add_heat(-40))
    #body2= Body(-2,1,34)
