# Generates hw5-jev-roc.json (ROC points and AUC for the Jev dev runs). Run from the repository root.
import json, re
import numpy as np
S = json.load(open("analysis/state/splits.json"))["narrates_or_overexplains"]["dev"]
LAB = {json.loads(l)["trace_id"]: json.loads(l)["label"] for l in open("analysis/state/hw5_labels/narrates_or_overexplains.jsonl")}
out = {}
for v in ("v3", "v4"):
    j = json.load(open(f"analysis/state/judges/narrates_or_overexplains-{v}.json"))
    crit = j["critiques"][j["prompt_hash"]]; pred = j["predictions"][j["prompt_hash"]]
    ids = [t for t in S if t in crit]
    score = np.array([max(float(x) for x in re.findall(r" ([0-9]+\.[0-9]+)", crit[t].split("Result:")[0])) for t in ids])  # P(Fail)
    y = np.array([LAB[t] for t in ids])  # 1 = Pass
    # the saved verdicts must match the 0.5 rule
    assert all((score[i] < 0.5) == (pred[t] == 1) for i, t in enumerate(ids)), v
    def roc(y, s):
        pts = []
        for th in [-1] + sorted(set(s)) + [2]:
            p = s < th  # judge says Pass when P(Fail) < threshold
            tpr = (p & (y == 1)).sum() / (y == 1).sum(); fpr = (p & (y == 0)).sum() / (y == 0).sum()
            pts.append((float(fpr), float(tpr), float(th)))
        pts = sorted(set(pts), key=lambda z: (z[0], z[1]))
        return pts
    def auc(y, s):  # P(score of a Fail > score of a Pass), ties count half
        f, p = s[y == 0], s[y == 1]
        return float(((f[:, None] > p[None, :]).sum() + 0.5 * (f[:, None] == p[None, :]).sum()) / (len(f) * len(p)))
    rng = np.random.default_rng(7); boots = []
    while len(boots) < 5000:
        i = rng.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(y): boots.append(auc(y[i], score[i]))
    pts = roc(y, score)
    # collapse to one point per (fpr,tpr), keeping the largest threshold range label
    uniq = {}
    for fpr, tpr, th in pts: uniq.setdefault((fpr, tpr), th)
    out[v] = dict(n=len(ids), pos=int((y == 1).sum()), neg=int((y == 0).sum()), auc=round(auc(y, score), 3),
                  auc_ci=[round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)],
                  roc=[[round(a, 4), round(b, 4), th] for (a, b), th in sorted(uniq.items())],
                  op=[round(float(((score < 0.5) & (y == 0)).sum() / (y == 0).sum()), 4), round(float(((score < 0.5) & (y == 1)).sum() / (y == 1).sum()), 4)],
                  scores=[[round(float(a), 2), int(b)] for a, b in zip(score, y)])
    print(v, out[v]["n"], "AUC", out[v]["auc"], out[v]["auc_ci"], "op", out[v]["op"], "points", len(out[v]["roc"]))
json.dump(out, open("analysis/report/figures/hw5-jev-roc.json", "w"))
