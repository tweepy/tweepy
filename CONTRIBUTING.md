



```sh
conda create -n tweepy-env python=3.7

conda activate tweepy-env
```

```sh
pip install ".[dev,test]" # need quotes?
```

```sh
python -m unittest discover tests
```
