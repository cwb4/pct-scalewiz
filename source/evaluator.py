"""Analyses the data and returns a tuple of results"""

import time
from pandas import DataFrame, Series

def evaluate(blanks, trials, baseline, xlim, ylim, interval):
    """Evaluates the data"""

    log = []
    def to_log(*msgs):
        """Appends strings to a list to be returned with the results_queue"""
        for msg in msgs:
            print(f"{msg}")
            log.append(f"{msg}")

    line = '\n' + '-'*75 + '\n'
    to_log("\nBeginning evaluation" + line*2)
    start=time.time()
    to_log(f"baseline: {round(baseline)} psi")
    to_log(f"xlim: {round(xlim*60)} s")
    to_log(f"ylim: {round(ylim)} psi")
    to_log(f"interval: {interval} s/reading ")

    max_measures = round(xlim*60/interval)
    total_area = round(ylim*max_measures)
    baseline_area = round(baseline*max_measures)
    avail_area = total_area - baseline_area

    to_log(f"total area: {total_area} psi")
    to_log(f"baseline area: {baseline_area} psi")
    to_log(f"avail area: {avail_area} psi")
    to_log(f"max measures: {max_measures}" + line)

    blank_scores = []
    blank_times = []

    for blank in blanks:
        blank_times.append(round(len(blank)*interval, 2))
        to_log(blank.name)
        measures = len(blank)
        to_log(f"blank duration: {round(measures*interval/60, 2)} min")
        to_log(f"number of measurements: {measures}")
        scale_area = blank.sum()
        to_log(f"scale area: {scale_area} psi")
        area_over_blank = ylim*len(blank) - scale_area
        to_log(f"area over blank: {area_over_blank} psi")
        protectable_area = round(avail_area - area_over_blank)
        to_log(f"protectable area: {protectable_area} psi\n")
        blank_scores.append(protectable_area)

    protectable_area = int(round(DataFrame(blank_scores).mean()))
    to_log(f"avg protectable area: {protectable_area} psi" + line)

    scores = {}
    for trial in trials:
        to_log(trial.name)
        measures = len(trial)
        to_log(f"trial duration: {round(measures*interval/60, 2)} min")
        to_log(f"number of measurements: {measures}")
        scale_area = round(trial.sum())
        to_log(f"scale area: {scale_area} psi")
        if measures < max_measures:
            to_log(f"Trial length {measures} measures is less than expected " +
                   f"{max_measures} for a passing run ")
            # ylim per would-be measure
            failure_region = round(ylim*(max_measures - measures))
        else:
            to_log(f"Trial length {measures} >= {max_measures} " +
                    "expected for a passing run")
            failure_region = 0
        to_log(f"Adding {failure_region} psi")
        to_log(f"Deducting baseline area {baseline_area} psi")
        scale_area = scale_area + failure_region - baseline_area
        to_log(f"scale area + failure region - baseline area: {scale_area} psi")
        scale_ratio = float(scale_area/protectable_area)
        to_log(f"scale ratio: {scale_ratio}")
        score = (1 - scale_ratio)*100
        if score > 100:
            to_log("Reducing score to 100%")
            score = 100
        to_log(f"score: {score:.2f}%" + line)
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
    to_log(line*2)
    to_log(f"Finished evaluation in {round(time.time() - start, 2)} s\n")
    return results_queue, log
