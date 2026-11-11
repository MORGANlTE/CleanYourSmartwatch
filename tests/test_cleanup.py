from cleanmywatch.cleanup import prepare


def test_keep_defaults_are_respected_and_no_mutation(adb):
    adb.states["com.microsoft.office.outlook"] = 0
    questions = []

    def keep(package, label, consequence):
        questions.append(package)
        return True

    report = prepare(adb, keep)
    assert questions == ["com.microsoft.office.outlook"]
    assert report["candidates"][0]["decision"] == "keep"
    assert report["plan"]["changes"] == []
    assert adb.calls == []


def test_declined_keep_produces_only_eligible_dry_run(adb):
    adb.states["com.microsoft.office.outlook"] = 0
    report = prepare(adb, lambda *args: False)
    assert report["plan"]["changes"][0]["package"] == "com.microsoft.office.outlook"
    assert adb.calls == []


def test_preloaded_candidate_stays_blocked(adb):
    adb.states["com.samsung.android.gallery.watch"] = 0
    adb.system_app = True
    report = prepare(adb, lambda *args: False)
    assert not report["candidates"][0]["executable"]
    assert "blocked_reason" in report["candidates"][0]
    assert report["plan"]["changes"] == []
    assert adb.calls == []
