"""Analyses the data and returns a tuple of results."""

import time
from pandas import DataFrame


def evaluate(proj, blanks, trials, baseline, xlim, ylim, interval):
    """Evaluate the data."""
    log = []

    def _log(*msgs):
        """Append string(s) to a list to be returned with the results_queue."""
        for msg in msgs:
            print(f"{msg}")
            log.append(f"{msg}")

    line = '\n' + '-'*75 + '\n'
    _log(f"\nBeginning evaluation of {proj}" + line*2)
    start = time.time()

    max_measures = round(xlim*60/interval)
    total_area = round(ylim*max_measures)
    baseline_area = round(baseline*max_measures)
    avail_area = total_area - baseline_area

    _log(f"baseline = {round(baseline)} psi")
    _log(f"time limit = {round(xlim*60)} s")
    _log(f"failing pressure threshold: {round(ylim)} psi")
    _log(f"reading interval = {interval} s/reading")
    _log(f"max measures = {round(xlim*60)} / {interval} = {max_measures}")
    _log(f"total area =  {ylim}*{max_measures} = {total_area} psi")
    _log("baseline area = baseline pressure * max measures")
    _log(f"baseline area = {baseline}*{max_measures} = {baseline_area} psi")
    _log("avail area = total area - baseline area")
    _log(f"avail area =  {total_area} - {baseline_area} = {avail_area} psi")
    _log(line)

    blank_scores = []
    blank_times = []

    for blank in blanks:
        blank = blank.dropna()
        blank_times.append(round(len(blank)*interval, 2))
        _log(blank.name)
        measures = len(blank)
        _log(f"blank duration = {round(measures*interval/60, 3)} min")
        _log(f"number of measurements = {measures}")
        _log(f"max psi = {int(round(blank.max()))}")
        scale_area = round(blank.sum())
        _log(f"scale area = sum of all pressure readings: {scale_area} psi")
        over_blank = ylim*measures - scale_area
        _log("area over blank = fail psi * measures - scale area")
        _log(f"area over blank = {ylim} * {measures} - {scale_area}")
        _log(f"area over blank = {over_blank} psi")
        protectable = round(avail_area - over_blank)
        _log("protectable area =  avail area - area over blank")
        _log(f"protectable area = {avail_area} - {over_blank}")
        _log(f"protectable area = {protectable} psi\n")
        blank_scores.append(protectable)

    protectable = int(round(DataFrame(blank_scores).mean()))
    _log(f"average protectable area: {protectable} psi" + line)

    scores = {}
    durations = []

    for trial in trials:
        trial = trial.dropna()
        _log(trial.name)
        measures = len(trial)
        duration = round(measures*interval/60, 3)
        if duration > xlim:
            _log(f"trial duration {duration} min is longer than {xlim} min")
            _log(f"truncating duration to {xlim} min (doesn't affect score)")
            duration = xlim
        durations.append(duration)
        _log(f"trial duration = {duration} min")
        _log(f"number of measurements = {measures}")
        scale_area = round(trial.sum())
        _log(f"max psi = {int(round(trial.max()))}")
        _log(f"scale area = sum of all pressure readings = {scale_area} psi")

        # check if this was a passing run or not
        if measures < max_measures:
            _log(
                f"trial length {measures} < {max_measures} expected " +
                "for a passing run"
            )
            # ylim per would-be measure
            failure_region = round(ylim*(max_measures - measures))
        else:
            _log(
                f"trial length {measures} >= {max_measures} expected " +
                "for a passing run"
            )
            failure_region = 0

        _log(f"failure region = {failure_region} psi")
        _log(f"deducting baseline area {baseline_area} psi")
        scale_area = scale_area + failure_region - baseline_area
        _log("new scale area =  scale area + failure region - baseline area")
        new_scale_text = f"{scale_area} + {failure_region} - {baseline_area}"
        _log("new scale area = " + new_scale_text)
        _log(f"new scale area = {scale_area} psi")
        scale_ratio = float(scale_area/protectable)
        _log(f"scale ratio = scale area / protectable area: {scale_ratio}")
        score = (1 - scale_ratio)*100
        if score > 100:
            _log("Negative scale ratio detected; reducing score to 100%")
            score = 100
        _log(f"score = (1 - scale ratio)*100: {score:.2f}%" + line)
        scores[trial.name] = score

    result_titles = [f"{i}" for i in scores]
    result_values = [
        f"{scores[i]:.1f}%"
        if scores[i] < 100  # say 100% not 100.0%
        else f"{scores[i]}%"
        for i in scores
    ]
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
    _log(line*2)
    _log(f"Finished evaluation in {round(time.time() - start, 3)} s\n")
    return results_queue, log
