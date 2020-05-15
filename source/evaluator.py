"""Analyses the data and returns a tuple of results"""

import time
from pandas import DataFrame, Series

def evaluate(proj, blanks, trials, baseline, xlim, ylim, interval):
    """Evaluates the data"""

    log = []
    def to_log(*msgs):
        """Appends strings to a list to be returned with the results_queue"""
        for msg in msgs:
            print(f"{msg}")
            log.append(f"{msg}")

    line = '\n' + '-'*75 + '\n'
    to_log(f"\nBeginning evaluation of {proj}" + line*2)
    start=time.time()
    to_log(f"baseline: {round(baseline)} psi")
    to_log(f"time limit: {round(xlim*60)} s")
    to_log(f"failing pressure threshold: {round(ylim)} psi")
    to_log(f"reading interval: {interval} s/reading ")

    max_measures = round(xlim*60/interval)
    total_area = round(ylim*max_measures)
    baseline_area = round(baseline*max_measures)
    avail_area = total_area - baseline_area

    to_log(f"total area =  {ylim} * {max_measures}: {total_area} psi")
    to_log(f"baseline area = {baseline} * {max_measures}: {baseline_area} psi")
    to_log(f"avail area = total area - baseline area: {avail_area} psi")
    to_log(f"max measures = {round(xlim*60)} / {interval}: {max_measures}")
    to_log(line)

    blank_scores = []
    blank_times = []

    for blank in blanks:
        blank = blank.dropna()
        blank_times.append(round(len(blank)*interval, 2))
        to_log(blank.name)
        measures = len(blank)
        to_log(f"blank duration: {round(measures*interval/60, 3)} min")
        to_log(f"number of measurements: {measures}")
        to_log(f"max psi: {int(round(blank.max()))}")
        scale_area = blank.sum()
        to_log(f"scale area = sum of all pressure readings: {scale_area} psi")
        over_blank = ylim*len(blank) - scale_area
        to_log(f"area over blank = {ylim}*{measures} - scale area: {over_blank} psi")
        protectable = round(avail_area - over_blank)
        to_log(f"protectable area =  avail area - area over blank: {protectable} psi\n")
        blank_scores.append(protectable)

    protectable = int(round(DataFrame(blank_scores).mean()))
    to_log(f"avg protectable area: {protectable} psi" + line)

    scores = {}
    durations = []

    for trial in trials:
        trial = trial.dropna()
        to_log(trial.name)
        measures = len(trial)
        duration = round(measures*interval/60, 3)
        if duration > xlim:
            to_log(f"Trial duration {duration} is longer than {xlim}")
            to_log(f"Truncating duration to {xlim} (does not affect score)")
            duration = xlim
        durations.append(duration)
        to_log(f"trial duration: {duration} min")
        to_log(f"number of measurements: {measures}")
        scale_area = round(trial.sum())
        to_log(f"max psi: {int(round(trial.max()))}")
        to_log(f"scale area = sum of all pressure readings: {scale_area} psi")
        if measures < max_measures:
            to_log(f"Trial length {measures} measures <= {max_measures} expected "+
                 "for a passing run")
            # ylim per would-be measure
            failure_region = round(ylim*(max_measures - measures))
        else:
            to_log(f"Trial length {measures} >= {max_measures} expected " +
                    "for a passing run")
            failure_region = 0
        to_log(f"Failure region: {failure_region} psi")
        to_log(f"Deducting baseline area {baseline_area} psi")
        scale_area = scale_area + failure_region - baseline_area
        to_log(f"scale area + failure region - baseline area: {scale_area} psi")
        scale_ratio = float(scale_area/protectable)
        to_log(f"scale ratio = scale area / protectable area: {scale_ratio}")
        score = (1 - scale_ratio)*100
        if score > 100:
            to_log("Negative scale ratio detected; reducing score to 100%")
            score = 100
        to_log(f"score = (1 - scale ratio)*100: {score:.2f}%" + line)
        scores[trial.name] = score

    result_titles = [f"{i}" for i in scores]
    result_values = [
                    f"{scores[i]:.1f}%"
                    if scores[i] < 100  # say 100% not 100.0%
                    else f"{scores[i]}%"
                    for i in scores
                    ]
    # durations = [round(len(trial)*interval, 2) for trial in trials]  #minutes
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
    to_log(line*2)
    to_log(f"Finished evaluation in {round(time.time() - start, 3)} s\n")
    return results_queue, log
