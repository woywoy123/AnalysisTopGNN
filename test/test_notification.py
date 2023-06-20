from AnalysisG.Notification import Notification


def test_notification():
    _nt = Notification()
    assert _nt.Success("test")
    assert _nt.Warning("test")
    assert _nt.Failure("test")


def test_notification_verbose3():
    print()
    _nt = Notification()
    _nt.Verbose = 3
    _nt.Caller = "tester"
    assert _nt.Success("!!!test")
    assert _nt.Warning("!!!test")
    assert _nt.Failure("!!!test")


def test_notification_verbose2():
    print()
    _nt = Notification()
    _nt.Verbose = 2
    _nt.Caller = "tester"
    assert _nt.Success("!!!test") == False
    assert _nt.Warning("!!!test")
    assert _nt.Failure("!!!test")


def test_notification_verbose1():
    _nt = Notification()
    _nt.Verbose = 1
    _nt.Caller = "tester"
    assert _nt.Success("!test")
    assert _nt.Warning("!!test")
    assert _nt.Failure("!!test")


def test_notification_verbose0():
    _nt = Notification()
    _nt.Verbose = 0
    _nt.Caller = "tester"
    assert _nt.Success("!test") == False
    assert _nt.Warning("!!test")
    assert _nt.Failure("!!test")


if __name__ == "__main__":
    test_notification()
    test_notification_verbose3()
    test_notification_verbose2()
    test_notification_verbose1()
    test_notification_verbose0()
    pass
