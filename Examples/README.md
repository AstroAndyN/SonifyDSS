# SonifyDSS Examples

Some example sonify-dss.py commands and their associated outputs

## Different sweeps of M51

A left-to-right sweep across M51. The DSS data is 400x400 pixels and 15 arcminutes across. The sound produced is 20 seconds long. A picture and "sweep" movie are created:

`python sonify-dss.py M51 15 M51-lr.wav 20 -d lr -siz 400 -pic M51.png -mov M51-lr.mp4`

Files produced:
* [M51-lr.wav](./M51-lr.wav)
* [M51.png](./M51.png)
* [M51-lr.mp4](./M51-lr.mp4)

As above but right-to-left (though no picture created as we already have it)

`python sonify-dss.py M51 15 M51-rl.wav 20 -d rl -siz 400 -mov M51-rl.mp4`

Files produced:
* [M51-rl.wav](./M51-rl.wav)
* [M51-rl.mp4](./M51-rl.mp4)

Ditto but top-to-bottom and bottom-to-top

`python sonify-dss.py M51 15 M51-tb.wav 20 -d tb -siz 400 -mov M51-tb.mp4`

`python sonify-dss.py M51 15 M51-bt.wav 20 -d bt -siz 400 -mov M51-bt.mp4`

Files produced:
* [M51-tb.wav](./M51-tb.wav)
* [M51-tb.mp4](./M51-tb.mp4)
* [M51-bt.wav](./M51-bt.wav)
* [M51-bt.mp4](./M51-bt.mp4)

### With clockwise and anticlockwise "sweeps"

`python sonify-dss.py M51 15 M51-clk.wav 20 -d clk -siz 400 -mov M51-clk.mp4`

`python sonify-dss.py M51 15 M51-aclk.wav 20 -d aclk -siz 400 -mov M51-aclk.mp4`

Files produced:
* [M51-clk.wav](./M51-clk.wav)
* [M51-clk.mp4](./M51-clk.mp4)
* [M51-aclk.wav](./M51-aclk.wav)
* [M51-aclk.mp4](./M51-aclk.mp4)

## M51 again, but "flipping" the frequency direction

```
python sonify-dss.py M51 15 M51-lr-ff.wav 20 -d lr -siz 400 -mov M51-lr-ff.mp4 -ff
python sonify-dss.py M51 15 M51-rl-ff.wav 20 -d rl -siz 400 -mov M51-rl-ff.mp4 -ff 
python sonify-dss.py M51 15 M51-tb-ff.wav 20 -d tb -siz 400 -mov M51-tb-ff.mp4 -ff 
python sonify-dss.py M51 15 M51-bt-ff.wav 20 -d bt -siz 400 -mov M51-bt-ff.mp4 -ff 
python sonify-dss.py M51 15 M51-clk-ff.wav 20 -d clk -siz 400 -mov M51-clk-ff.mp4 -ff 
python sonify-dss.py M51 15 M51-aclk-ff.wav 20 -d aclk -siz 400 -mov M51-aclk-ff.mp4 -ff 
```

Files produced:
* [M51-lr-ff.wav](./M51-lr-ff.wav)
* [M51-lr-ff.mp4](./M51-lr-ff.mp4)
* [M51-rl-ff.wav](./M51-rl-ff.wav)
* [M51-rl-ff.mp4](./M51-rl-ff.mp4)
* [M51-tb-ff.wav](./M51-tb-ff.wav)
* [M51-tb-ff.mp4](./M51-tb-ff.mp4)
* [M51-bt-ff.wav](./M51-bt-ff.wav)
* [M51-bt-ff.mp4](./M51-bt-ff.mp4)
* [M51-clk-ff.wav](./M51-clk-ff.wav)
* [M51-clk-ff.mp4](./M51-clk-ff.mp4)
* [M51-aclk-ff.wav](./M51-aclk-ff.wav)
* [M51-aclk-ff.mp4](./M51-aclk-ff.mp4)


## Different object NGC4565

All the sets above but for the edge-on galaxy NGC4565

```
python sonify-dss.py NGC4565 15 NGC4565-lr.wav 20 -d lr -siz 400 -mov NGC4565-lr.mp4 -pic NGC4565.png
python sonify-dss.py NGC4565 15 NGC4565-lr-ff.wav 20 -d lr -siz 400 -mov NGC4565-lr-ff.mp4 -ff
python sonify-dss.py NGC4565 15 NGC4565-rl.wav 20 -d rl -siz 400 -mov NGC4565-rl.mp4 
python sonify-dss.py NGC4565 15 NGC4565-rl-ff.wav 20 -d rl -siz 400 -mov NGC4565-rl-ff.mp4 -ff 
python sonify-dss.py NGC4565 15 NGC4565-tb.wav 20 -d tb -siz 400 -mov NGC4565-tb.mp4 
python sonify-dss.py NGC4565 15 NGC4565-tb-ff.wav 20 -d tb -siz 400 -mov NGC4565-tb-ff.mp4 -ff 
python sonify-dss.py NGC4565 15 NGC4565-bt.wav 20 -d bt -siz 400 -mov NGC4565-bt.mp4 
python sonify-dss.py NGC4565 15 NGC4565-bt-ff.wav 20 -d bt -siz 400 -mov NGC4565-bt-ff.mp4 -ff 
python sonify-dss.py NGC4565 15 NGC4565-clk.wav 20 -d clk -siz 400 -mov NGC4565-clk.mp4 
python sonify-dss.py NGC4565 15 NGC4565-clk-ff.wav 20 -d clk -siz 400 -mov NGC4565-clk-ff.mp4 -ff 
python sonify-dss.py NGC4565 15 NGC4565-aclk.wav 20 -d aclk -siz 400 -mov NGC4565-aclk.mp4 
python sonify-dss.py NGC4565 15 NGC4565-aclk-ff.wav 20 -d aclk -siz 400 -mov NGC4565-aclk-ff.mp4 -ff 
```
Files:

* [NGC4565-lr.wav](./NGC4565-lr.wav)
* [NGC4565-lr.mp4](./NGC4565-lr.mp4)
* [NGC4565.png](./NGC4565.png)
* [NGC4565-lr-ff.wav](./NGC4565-lr-ff.wav)
* [NGC4565-lr-ff.mp4](./NGC4565-lr-ff.mp4)
* [NGC4565-rl.wav](./NGC4565-rl.wav)
* [NGC4565-rl.mp4](./NGC4565-rl.mp4)
* [NGC4565-rl-ff.wav](./NGC4565-rl-ff.wav)
* [NGC4565-rl-ff.mp4](./NGC4565-rl-ff.mp4)
* [NGC4565-tb.wav](./NGC4565-tb.wav)
* [NGC4565-tb.mp4](./NGC4565-tb.mp4)
* [NGC4565-tb-ff.wav](./NGC4565-tb-ff.wav)
* [NGC4565-tb-ff.mp4](./NGC4565-tb-ff.mp4)
* [NGC4565-bt.wav](./NGC4565-bt.wav)
* [NGC4565-bt.mp4](./NGC4565-bt.mp4)
* [NGC4565-bt-ff.wav](./NGC4565-bt-ff.wav)
* [NGC4565-bt-ff.mp4](./NGC4565-bt-ff.mp4)
* [NGC4565-clk.wav](./NGC4565-clk.wav)
* [NGC4565-clk.mp4](./NGC4565-clk.mp4)
* [NGC4565-clk-ff.wav](./NGC4565-clk-ff.wav)
* [NGC4565-clk-ff.mp4](./NGC4565-clk-ff.mp4)
* [NGC4565-aclk.wav](./NGC4565-aclk.wav)
* [NGC4565-aclk.mp4](./NGC4565-aclk.mp4)
* [NGC4565-aclk-ff.wav](./NGC4565-aclk-ff.wav)
* [NGC4565-aclk-ff.mp4](./NGC4565-aclk-ff.mp4)

## Changing the frequency range

Lowering the frequency range to 3HZ-to-500HZ for M51, clockwise sweep with and without frequency "flip":

```
python sonify-dss.py M51 15 M51-clk-3Hz500Hz.wav 20 -d clk -siz 400 -mov M51-clk-3Hz500Hz.mp4 -lf 3 -hf 500
python sonify-dss.py M51 15 M51-clk-3Hz500Hz-ff.wav 20 -d clk -siz 400 -mov M51-clk-3Hz500Hz-ff.mp4 -lf 3 -hf 500 -ff
```

Files:
* [M51-clk-3Hz500Hz.wav](./M51-clk-3Hz500Hz.wav)
* [M51-clk-3Hz500Hz.mp4](./M51-clk-3Hz500Hz.mp4)
* [M51-clk-3Hz500Hz-ff.wav](./M51-clk-3Hz500Hz-ff.wav)
* [M51-clk-3Hz500Hz-ff.mp4](./M51-clk-3Hz500Hz-ff.mp4)

And similarly but raise the frequency range to 100Hz-to-2000Hz:

```
python sonify-dss.py M51 15 M51-clk-100Hz2000Hz.wav 20 -d clk -siz 400 -mov M51-clk-100Hz2000Hz.mp4 -lf 100 -hf 2000
python sonify-dss.py M51 15 M51-clk-100Hz2000Hz-ff.wav 20 -d clk -siz 400 -mov M51-clk-100Hz2000Hz-ff.mp4 -lf 100 -hf 2000 -ff
```

Files:
* [M51-clk-100Hz2000Hz.wav](./M51-clk-100Hz2000Hz.wav)
* [M51-clk-100Hz2000Hz.mp4](./M51-clk-100Hz2000Hz.mp4)
* [M51-clk-100Hz2000Hz-ff.wav](./M51-clk-100Hz2000Hz-ff.wav)
* [M51-clk-100Hz2000Hz-ff.mp4](./M51-clk-100Hz2000Hz-ff.mp4)


