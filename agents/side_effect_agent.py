from typing import Any


class SideEffectAgent:

    def analyze(self, study: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze adverse events from a parsed clinical trial.

        The complete ClinicalTrials.gov response is stored inside
        study["raw_data"] by DocumentParser.
        """

        nct_id = study.get("nct_id", "")

        # ---------------------------------------------------------
        # Get the original ClinicalTrials.gov response
        # ---------------------------------------------------------

        raw_data = study.get("raw_data", {})

        if not isinstance(raw_data, dict):
            raw_data = {}

        # ---------------------------------------------------------
        # Get results section
        # ---------------------------------------------------------

        results_section = raw_data.get(
            "resultsSection",
            {}
        )

        if not isinstance(results_section, dict):
            results_section = {}

        # ---------------------------------------------------------
        # Get adverse events module
        # ---------------------------------------------------------

        adverse_events_module = results_section.get(
            "adverseEventsModule",
            {}
        )

        if not isinstance(adverse_events_module, dict):
            adverse_events_module = {}

        # ---------------------------------------------------------
        # Extract serious adverse events
        # ---------------------------------------------------------

        serious_events = adverse_events_module.get(
            "seriousEvents",
            []
        )

        if not isinstance(serious_events, list):
            serious_events = []

        # ---------------------------------------------------------
        # Extract other/non-serious adverse events
        # ---------------------------------------------------------

        other_events = adverse_events_module.get(
            "otherEvents",
            []
        )

        if not isinstance(other_events, list):
            other_events = []

        # ---------------------------------------------------------
        # Store event names
        # ---------------------------------------------------------

        serious_event_names = []
        other_event_names = []

        # ---------------------------------------------------------
        # Serious events
        # ---------------------------------------------------------

        for event in serious_events:

            if not isinstance(event, dict):
                continue

            term = event.get("term", "")

            if term:
                serious_event_names.append(term)

        # ---------------------------------------------------------
        # Other events
        # ---------------------------------------------------------

        for event in other_events:

            if not isinstance(event, dict):
                continue

            term = event.get("term", "")

            if term:
                other_event_names.append(term)

        # ---------------------------------------------------------
        # Combine events
        # ---------------------------------------------------------

        all_events = []

        for event in serious_event_names:
            if event not in all_events:
                all_events.append(event)

        for event in other_event_names:
            if event not in all_events:
                all_events.append(event)

        # ---------------------------------------------------------
        # Fallback
        #
        # Useful if manually supplied test data contains
        # "adverse_events".
        # ---------------------------------------------------------

        if not all_events:

            fallback_events = study.get(
                "adverse_events",
                []
            )

            if isinstance(fallback_events, list):
                all_events = [
                    str(event)
                    for event in fallback_events
                    if event
                ]

        # ---------------------------------------------------------
        # Extract frequency threshold
        # ---------------------------------------------------------

        frequency_threshold = adverse_events_module.get(
            "frequencyThreshold",
            ""
        )

        # ---------------------------------------------------------
        # Extract timeframe
        # ---------------------------------------------------------

        timeframe = adverse_events_module.get(
            "timeFrame",
            ""
        )

        # ---------------------------------------------------------
        # Build response
        # ---------------------------------------------------------

        return {
            "agent": "side_effect",

            "nct_id": nct_id,

            "adverse_event_count": len(all_events),

            "adverse_events": all_events,

            "serious_event_count": len(
                serious_event_names
            ),

            "serious_events": serious_event_names,

            "other_event_count": len(
                other_event_names
            ),

            "other_events": other_event_names,

            "frequency_threshold": frequency_threshold,

            "time_frame": timeframe,
        }