class DeviceModel:
    def __init__(self, model, manufacturer):
        self.model = model
        self.manufacturer = manufacturer

    def __str__(self):
        return f"{self.manufacturer} {self.model}"

    def to_dict(self):
        return {
            "model": self.model,
            "manufacturer": self.manufacturer
        }

