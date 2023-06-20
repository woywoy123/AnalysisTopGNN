from .Notification import Notification
from AnalysisTopGNN.Tools.Tables import Tables


class Optimization(Notification):
    def __init__(self):
        pass

    def CheckGivenSample(self, sample):
        if len(sample) == 0:
            msg = "Samples have not been compiled. Rerun with 'DataCache = True' and try again."
            self.Failure("=" * len(msg))
            self.FailureExit(msg)

        for i in sample:
            self.Success(
                "(Nodes) -> '" + i + "' Number of Graphs: " + str(len(sample[i]))
            )

    def TrainingNodes(self, Nodes):
        msg = "(" + str(Nodes) + ") ->" + str(len(self._Samples[Nodes]))
        self.Success("=" * len(msg))
        self.Success(msg)

    def StartKfoldInfo(self, train, valid, kfold, folds):
        msg = (
            "Training Size: "
            + str(len(train))
            + " Validation Size: "
            + str(len(valid))
            + " @ Batch Size: "
            + str(self.BatchSize)
        )
        self.Success("=" * len(msg))
        self.Success("kFold: " + str(kfold + 1) + " / " + str(folds))
        self.Success(msg)
        self.Success("=" * len(msg))
        self._it = 0

    def TrainingInfo(self, lengthdata, epoch, pred, truth, loss_acc, debug):
        per = int(100 * self._it / lengthdata)
        if per % self.VerbosityIncrement == 0:
            self.Success("!!==> Progress: " + str(per) + "%")
        self._it += 1
        if debug == False:
            return

        if "loss" in debug:
            for i in loss_acc:
                self.Success("Loss (" + i + ") -> " + str(loss_acc[i][0].item()))
            self.Success("Loss (Total Loss) -> " + str(epoch.TotalLoss.item()))

        if "accuracy" in debug:
            for i in loss_acc:
                self.Success("Accuracy (" + i + ") -> " + str(loss_acc[i][1].item()))

        if "compare" in debug:
            c_names = self.Model.GetModelClassifiers(self.Model._model)
            Tbl = Tables()
            Tbl.Sum = False
            Tbl.Title = "Prediction Comparison Table"
            Tbl.AddColumnTitle("Index")

            for i in c_names:
                p_ = pred[i[2:]]
                t_ = truth[i[2:]].view(-1)
                if c_names[i]:
                    p_ = p_.max(1)[1]

                Tbl.AddColumnTitle("Pr (" + i[2:] + ")")
                Tbl.AddColumnTitle("Tr (" + i[2:] + ")")
                Tbl.AddColumnTitle("Co (" + i[2:] + ")")
                k = 0
                for t, j, c in zip(t_.tolist(), p_.tolist(), (p_ - t_).tolist()):
                    Tbl.AddValues(k, "Pr (" + i[2:] + ")", t)
                    Tbl.AddValues(k, "Tr (" + i[2:] + ")", j)
                    Tbl.AddValues(k, "Co (" + i[2:] + ")", c)
                    k += 1
                Tbl.Compile()
                print("\n".join(Tbl.output))

    def ShowEpoch(self, Epoch, Epochs):
        self.Success(
            "_" * 10
            + " Starting Epoch "
            + str(Epoch + 1)
            + "/"
            + str(Epochs)
            + "_" * 10
        )

    def FileNotFoundWarning(self, Directory, Name):
        pass
