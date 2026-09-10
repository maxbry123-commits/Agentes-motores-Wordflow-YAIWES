# Fact vs interpretation vs hypothesis (inserted into the prompt)

In output artifacts, **explicitly** separate three levels:

- **Fact**: what the respondent said or did. A verbatim quote, a behavioral observation. Tag it `[fact]` when the context isn't obvious.
- **Interpretation**: what it might mean. Tag it `[interpretation]`. Don't present it as fact.
- **Hypothesis**: what needs further verification. Tag it `[hypothesis]`. It must be falsifiable.

Example:

> [fact] Respondent R03 returned to the menu three times after pressing the first button.
> [interpretation] The respondent may not trust the result and is looking for confirmation.
> [hypothesis] If we remove the first step, the share of "returns" within 30 seconds of the first click will drop.

Without an explicit separation, it's easy to end up with a report where hypotheses look like facts and interpretations leak into recommendations without any grounding.
