subjects = input().split()
marks = input().split()
if len(subjects) != len(marks):
    print("Mismatch")
else:
    print(f"{'No':<4}{'Subject':<12}{'Marks':>5}  Result")
    passed = 0
    for n, (subject, mark) in enumerate(zip(subjects, marks), start=1):
        ok = int(mark) >= 40
        passed += ok
        print(f"{n:<4}{subject:<12}{int(mark):>5}  {'PASS' if ok else 'FAIL'}")
    print(f"Passed {passed} of {len(subjects)}")
    overall = all(int(m) >= 40 for m in marks)
    print(f"Overall: {'PASS' if overall else 'FAIL'}")
