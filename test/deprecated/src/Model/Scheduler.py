from torch.optim.lr_scheduler import ExponentialLR, CyclicLR


class Scheduler:
    def __init__(self, optimizer, keyword, parameters):
        parameters["optimizer"] = optimizer
        self.scheduler = None
        self.scheduler = (
            self.ExponentialLR(parameters)
            if keyword == "ExponentialLR"
            else self.scheduler
        )
        self.scheduler = (
            self.CyclicLR(parameters) if keyword == "CyclicLR" else self.scheduler
        )

    def ExponentialLR(self, params):
        return ExponentialLR(**params)

    def CyclicLR(self, params):
        params["cycle_momentum"] = False
        return CyclicLR(**params)

    def __call__(self):
        self.scheduler.step()
