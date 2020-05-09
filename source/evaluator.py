"""Analyses the data and returns a tuple of results"""

import time
from pandas import DataFrame, Series

def evaluate(blanks, trials, baseline, xlim, ylim, interval):
    """Evaluates the data"""

    log = []
    def to_log(*msgs):
        for msg in msgs:
            print(f"{msg}")
            log.append(f"{msg}")

    to_log("\nBeginning evaluation\n")
    start=time.time()
    to_log(f"baseline: {baseline} psi")
    to_log(f"xlim: {xlim*60} s")
    to_log(f"ylim: {ylim} psi\n")

    total_area = ylim*xlim*60/interval
    baseline_area = baseline*xlim*60/interval
    avail_area = total_area - baseline_area
    to_log(f"total_area: {total_area} psi")
    to_log(f"baseline_area: {baseline_area} psi")
    to_log(f"avail_area: {avail_area} psi")
    to_log(f"max measures: {xlim*60/interval}\n")

    blank_scores = []
    blank_times = []

    for blank in blanks:
        blank_times.append(round(len(blank)*interval, 2))
        to_log(blank.name)
        scale_area = blank.sum()
        to_log(f"scale area: {scale_area} psi")
        area_over_blank = ylim*len(blank) - scale_area
        to_log(f"area over blank: {area_over_blank} psi")
        protectable_area = round(avail_area - area_over_blank)
        to_log(f"protectable_area: {protectable_area} psi")
        blank_scores.append(protectable_area)
        to_log()
    protectable_area = float(DataFrame(blank_scores).mean())
    to_log(f"avg protectable_area: {protectable_area} psi\n")

    scores = {}
    for trial in trials:
        to_log(trial.name)
        measures = len(trial)
        to_log(f"number of measurements: {measures}")
        to_log(f"total trial area: {trial.sum()} psi")
        # all the area under the curve + ylim per would-be measure
        scale_area = round(trial.sum() + ylim*(xlim*60/interval - measures))
        to_log(f"scale area {scale_area} psi")
        score = float((1 - (scale_area - baseline_area)/protectable_area)*100)
        if score > 100:
            to_log("Reducing score to 100%")
            score = 100
        to_log(f"score: {score:.2f}%\n")
        scores[trial.name] = score
        to_log()

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

    to_log(f"\nFinished evaluation in {round(time.time() - start, 2)} s\n")
    return results_queue, log
