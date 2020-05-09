"""Docstring"""

def evaluate(blanks, trials, baseline, xlim, ylim, interval):
    """Evaluates the data"""

    start=time.time()
    print("Evaluating data")
    print(f"baseline: {baseline} psi")
    print(f"xlim: {xlim*60} s")
    print(f"ylim: {ylim} psi\n")

    total_area = ylim*xlim*60/interval
    baseline_area = baseline*xlim*60/interval
    avail_area = total_area - baseline_area
    print(f"total_area: {total_area} psi")
    print(f"baseline_area: {baseline_area} psi")
    print(f"avail_area: {avail_area} psi")
    print(f"max measures: {xlim*60/interval}\n")

    blank_scores = []
    blank_times = []

    for blank in blanks:
        blank_times.append(round(len(blank)*interval, 2))
        print(blank.name)
        scale_area = blank.sum()
        print(f"scale area: {scale_area} psi")
        area_over_blank = ylim*len(blank) - scale_area
        print(f"area over blank: {area_over_blank} psi")
        protectable_area = round(avail_area - area_over_blank)
        print(f"protectable_area: {protectable_area} psi")
        blank_scores.append(protectable_area)
        print()
    protectable_area = round(DataFrame(blank_scores).mean())
    print(f"avg protectable_area: {protectable_area} psi\n")

    scores = {}
    for trial in trials:
        print(trial.name)
        measures = len(trial)
        print(f"number of measurements: {measures}")
        print(f"total trial area: {round(trial.sum())} psi")
        # all the area under the curve + ylim per would-be measure
        scale_area = round(trial.sum() + ylim*(xlim*60/interval - measures))
        print(f"scale area {scale_area} psi")
        score = (1 - (scale_area - baseline_area)/protectable_area)*100
        print(f"score: {score:.2f}%")
        if score > 100:
            print("Reducing score to 100%")
            score = 100
        scores[trial.name] = score
        print()

    result_titles = [f"{i}" for i in scores]
    result_values = [f"{scores[i]:.1f}%" for i in scores]
    durations = [round(len(trial)*interval, 2) for trial in trials]
    max_psis = [
                round(trial.max())
                if round(trial.max()) <= ylim
                else ylim
                for trial in trials
               ]

    results_queue = (
            blank_times,
            result_titles,
            result_values,
            durations,
            baseline,
            ylim,
            max_psis
    )

    print(f"Finished evaluation in {round(time.time() - start, 2)} s\n")
    return results_queue
