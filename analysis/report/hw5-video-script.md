 
Record your screen for up to 5 minutes in one continuous take. Walk through your failure mode, one development disagreement and how you responded, and your test TPR, TNR, and confidence intervals. Explain whether you would use the judge. Recalculate test metrics from saved predictions live on camera.


# HW5 video script (≤ 5 minutes, one take)

Spoken lines are plain text; *[screen: …]* are the actions. About 600 spoken words, which leaves room for the demo. The two decisions in brackets are yours: pick one line or write your own.

Before recording: start the review app (`uv run python -m analysis.review_app.server`), and open `analysis/prompts/narrates_or_overexplains-v2.txt`, `analysis/report/hw5-log.md` and a terminal at the repository root.

---

## 0:00–0:35 · The failure mode

*[screen: `patterns.json`, the `narrates_or_overexplains` definition]*

My judge detects one failure mode from Homework 4: narrates or overexplains. The question is: does Cartwheel's final reply state the result directly, answer first, without narrating its own process or explaining more than the user needs?

It fails when the reply narrates its lookups, adds information nobody asked for, explains policy beyond a one-line reason, sounds grudging, guesses, or buries the answer after details. That last one is the "bottom line up front" rule I added during labeling. Order details, IDs and a short reason are always fine.

## 0:35–1:05 · Labels and split

*[screen: `hw5_labels/narrates_or_overexplains.jsonl`, then `splits.json` counts]*

I have 99 labeled conversations, one per conversation: 58 Pass and 41 Fail, with Pass as 1. I split them 20/40/40 with a fixed seed: 20 for training examples, 39 for development and 40 held out for test, with 17 Fails in test. The judge input holds only the conversation. No labels, notes or scenario metadata.

## 1:05–1:35 · Prompt and model

*[screen: the prompt file, scroll through definitions, examples and output format]*

The prompt has the task, the six Fail rules, the always-allowed list, four training examples (a clear Pass, a clear Fail and two borderline cases), and a critique-then-verdict output. I compared three GPT-5.6 models on the same prompt on dev and picked gpt-5.6-terra. It caught all 16 dev Fails, at about half the per-token price of the largest model.

## 1:35–3:00 · One development disagreement

*[screen: review app, `wl-hw5-dev-v1`, trace b1dd5bac, Labels panel with the judge critique open]*

Here's a disagreement from my first dev run. A support user asks, "just give me the price already." The reply says, "I found multiple products named Heavy-Duty Vase, so the price depends on the listing," and lists the prices.

I labeled it Pass. The judge said Fail. Its critique calls "the listed prices I found" narration of the search.

I had three options: fix my label, clarify the definition, or fix the prompt. My definition says narration means describing *how* you looked, not using the word "found" to present results. So the judge was wrong, and I revised the prompt to say that.

*[screen: `hw5-log.md`, the v5 and v6 rows]*

That fixed this trace, but it had a side effect. The judge started treating "I found…" as an excuse for replies that put the answer late, and three real Fails slipped through. My second and last revision says "I found" settles only the narration rule; the answer still has to come first. On dev, that version, v6, agreed with every human Pass and 14 of 16 Fails. I stopped there because the handout allows two revisions, and further tuning on 39 traces risks fitting the dev set.

## 3:00–4:05 · Test results, recalculated live

*[screen: terminal, run the command below]*

I froze v6 and ran it once on the 40 test traces. Let me recompute the metrics from the saved predictions.

```bash
uv run python -c "
import json
from analysis.helpers.tools import _wilson_interval as wilson
j=json.load(open('analysis/state/judges/narrates_or_overexplains-v6.json')); p=j['predictions'][j['prompt_hash']]
lab={json.loads(l)['trace_id']:json.loads(l)['label'] for l in open('analysis/state/hw5_labels/narrates_or_overexplains.jsonl')}
test=json.load(open('analysis/state/splits.json'))['narrates_or_overexplains']['test']
tp=sum(lab[t]==1 and p[t]==1 for t in test); fn=sum(lab[t]==1 and p[t]==0 for t in test)
tn=sum(lab[t]==0 and p[t]==0 for t in test); fp=sum(lab[t]==0 and p[t]==1 for t in test)
print(f'TP={tp} FN={fn} TN={tn} FP={fp}')
print(f'TPR={tp/(tp+fn):.3f} {wilson(tp,tp+fn)}  TNR={tn/(tn+fp):.3f} {wilson(tn,tn+fp)}')"
```

Expected output: `TP=21 FN=2 TN=12 FP=5` and `TPR=0.913 [0.732, 0.9758]  TNR=0.706 [0.4687, 0.8672]`.

Pass is the positive class. TPR is 21 of 23: when I say Pass, the judge agrees 91% of the time, with a 95% interval of 73 to 98%. TNR is 12 of 17: it catches 71% of real failures, and the interval runs from 47 to 87%. That interval is wide because there are only 17 Fails. Four of the five missed failures are policy over-explanation, like explaining that a store uses the platform default when the merchant only asked for the window.

## 4:05–4:45 · Would I use it?

*[screen: the test JSON or the log's test section]*

[Choose one, or write your own.]

- **Not yet, for monitoring:** "I would use this judge to flag replies for review, since it rarely flags a good reply. I would not use it alone to monitor this failure: it may miss anywhere from 1 in 8 to over half of real failures. Next I would tighten the policy rule and validate on new labeled traces, since this test set is used up."
- **Yes, with a correction:** "I would use it for tracking trends. Its errors are measured, so I can correct its Fail rate. On the unlabeled traces it flags 32% and the corrected estimate is 38%, from 16 to 66%, with the caveat that the interval is wide."

## 4:45–5:00 · Close

That's my narrates-or-overexplains judge: one failure mode, validated on held-out data, with the numbers and their uncertainty. Thanks.
