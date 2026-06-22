# Route B BEM v3.1 with SSTcore ideal.txt loader

This is BEM v3 plus direct loading of ideal-knot Fourier data from the installed `SSTcore` package.

It keeps the BEM v3 backend:

\[
S_{ij}=\sqrt{A_i}\,G(x_i,x_j)\sqrt{A_j},
\]

parallel-transport tube frames, and screened self-patch terms.

## Install SSTcore

```bash
pip install SSTcore
```

## List available ideal.txt blocks

```bash
python routeB_RT_bem_v3_1_sstcore_falsifier.py --source sstcore --list-sstcore-knots --sstcore-max-knots 50
```

## Run default controls from SSTcore

This loads:

```text
0:1:1, 3:1:1, 4:1:1
```

from `SSTcore.get_ideal_txt_path()`.

```bash
python routeB_RT_bem_v3_1_sstcore_falsifier.py --source sstcore --outdir outputs_routeB_SSTcore
```

## Run multiple knots from SSTcore

```bash
python routeB_RT_bem_v3_1_sstcore_falsifier.py \
  --source sstcore \
  --sstcore-knot-ids 0:1:1,3:1:1,4:1:1,5:1:1,5:2:1,6:1:1,6:2:1,6:3:1 \
  --outdir outputs_routeB_SSTcore_many
```

## Run all first N single-component ideal blocks

```bash
python routeB_RT_bem_v3_1_sstcore_falsifier.py   --source file --ideal ideal.txt    --sstcore-knot-ids all   --sstcore-max-knots 20   --outdir outputs_routeB_SSTcore_all20
```

## Use a local coordinate ideal.txt instead

```bash
python routeB_RT_bem_v3_1_sstcore_falsifier.py --source file --ideal ideal.txt --outdir outputs_routeB_file
```

## Output

When using SSTcore, the script writes the sampled coordinates it actually used to:

```text
<outdir>/sstcore_sampled_ideal_used.txt
```

This lets you reproduce the exact sampled input without relying on import state.

## Reminder

Passing all gates does not derive alpha. It only means this Route-B BEM v3.1 candidate survives the chosen falsifiers. A theorem-level map

\[
\alpha^{-1}=F(S_{RT}(3_1))
\]

must still be specified before any comparison with CODATA.