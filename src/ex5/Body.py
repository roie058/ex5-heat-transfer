class Body:
    def __init__(self, mass: float, heat_capacity: float, temperature: float):
        if mass <= 0 or heat_capacity <= 0 or temperature < 0:
            raise ValueError("Mass and heat capacity must be > 0, and temperature must be >= 0")

        self.mass = mass
        self.heat_capacity = heat_capacity
        self.temperature = temperature

    def add_heat(self, heat: float) -> float:
        delta_t = heat / (self.mass * self.heat_capacity)
        self.temperature = self.temperature + delta_t
        return self.temperature


if __name__ == "__main__":
    body1 = Body(100, 0.15, 200)
    print(body1.add_heat(20))
    print(body1.add_heat(-40))
