"""Analyses the data and returns a tuple of results"""

import time
from pandas import DataFrame, Series

def evaluate(blanks, trials, baseline, xlim, ylim, interval):
    """Evaluates the data"""

    log = []
    def log(*msgs):
        """Appends strings to a list to be returned with the results_queue"""
        for msg in msgs:
            print(f"{msg}")
            log.append(f"{msg}")

    line = '\n' + '-'*75 + '\n'
    log("\nBeginning evaluation" + line*2)
    start=time.time()
    log(f"baseline: {round(baseline)} psi")
    log(f"time limit: {round(xlim*60)} s")
    log(f"failing pressure threshold: {round(ylim)} psi")
    log(f"reading interval: {interval} s/reading ")

    max_measures = round(xlim*60/interval)
    total_area = round(ylim*max_measures)
    baseline_area = round(baseline*max_measures)
    avail_area = total_area - baseline_area

    log(f"total area =  {ylim} * {max_measures}: {total_area} psi")
    log(f"baseline area = {max_measures} * {ylim}: {baseline_area} psi")
    log(f"avail area = total area - baseline area: {avail_area} psi")
    log(f"max measures = {round(xlim*60)} / {interval}: {max_measures}")
    log(line)

    blank_scores = []
    blank_times = []

    for blank in blanks:
        blank_times.append(round(len(blank)*interval, 2))
        log(blank.name)
        measures = len(blank)
        log(f"blank duration: {round(measures*interval/60, 2)} min")
        log(f"number of measurements: {measures}")
        log(f"max psi: {round(blank.max())}")
        scale_area = blank.sum()
        log(f"scale area = sum of all pressure readings: {scale_area} psi")
        over_blank = ylim*len(blank) - scale_area
        log(f"area over blank = {ylim}*{measures} - scale area: {over_blank} psi")
        protectable = round(avail_area - over_blank)
        log(f"protectable area =  avail area - area over blank: {protectable} psi\n")
        blank_scores.append(protectable)

    protectable = int(round(DataFrame(blank_scores).mean()))
    log(f"avg protectable area: {protectable} psi" + line)

    scores = {}
    for trial in trials:
        log(trial.name)
        measures = len(trial)
        log(f"trial duration: {round(measures*interval/60, 2)} min")
        log(f"number of measurements: {measures}")
        scale_area = round(trial.sum())
        log(f"max psi: {round(trial.max())}")
        log(f"scale area = sum of all pressure readings: {scale_area} psi")
        if measures < max_measures:
            log(f"Trial length {measures} measures <= {max_measures} expected "+
                 "for a passing run")
            # ylim per would-be measure
            failure_region = round(ylim*(max_measures - measures))
        else:
            log(f"Trial length {measures} >= {max_measures} expected " +
                    "for a passing run")
            failure_region = 0
        log(f"Failure region: {failure_region} psi")
        log(f"Deducting baseline area {baseline_area} psi")
        scale_area = scale_area + failure_region - baseline_area
        log(f"scale area + failure region - baseline area: {scale_area} psi")
        scale_ratio = float(scale_area/protectable)
        log(f"scale ratio = scale area / protectable area: {scale_ratio}")
        score = (1 - scale_ratio)*100
        if score > 100:
            log("Negative scale ratio detected; reducing score to 100%")
            score = 100
        log(f"score = (1 - scale ratio)*100: {score:.2f}%" + line)
        scores[trial.name] = score

    result_titles = [f"{i}" for i in scores]
    result_values = [f"{scores[i]:.1f}%" for i in scores]
    durations = [round(len(trial)*interval, 2) for trial in trials]  #minutes
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
    log(line*2)
    log(f"Finished evaluation in {round(time.time() - start, 2)} s\n")
    return results_queue, log
