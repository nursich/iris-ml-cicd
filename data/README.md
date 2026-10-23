# Dataset: Iris (UCI Machine Learning Repository)

| Field        | Value |
|--------------|-------|
| Source       | UCI Machine Learning Repository, dataset #53 |
| URL          | https://archive.ics.uci.edu/dataset/53/iris |
| DOI          | https://doi.org/10.24432/C56C76 |
| Creator      | R. A. Fisher (1936) |
| License      | CC BY 4.0 |
| Instances    | 150 (50 per class) |
| Features     | 4 continuous features, in centimetres |
| Classes      | Iris-setosa, Iris-versicolor, Iris-virginica |

## Columns in `iris.csv`

| Column            | Meaning |
|-------------------|---------|
| `sepal_length_cm` | Sepal length, cm |
| `sepal_width_cm`  | Sepal width, cm |
| `petal_length_cm` | Petal length, cm |
| `petal_width_cm`  | Petal width, cm |
| `species`         | Class label |

## Notes on data integrity

The UCI page documents two transcription errors in the original
`iris.data` file (samples 35 and 38). This repository uses the corrected
values given on the UCI page, which match Fisher's 1936 paper:

* sample 35: `4.9, 3.1, 1.5, 0.2, Iris-setosa`
* sample 38: `4.9, 3.6, 1.4, 0.1, Iris-setosa`

The SHA-256 checksum of `iris.csv` is checked by the unit tests
(`tests/test_data.py`), so any accidental change to the data breaks the
CI pipeline. This is a simple way to guarantee that every experiment
runs on exactly the same data.

```
7866a81bd4601f74577a9cd0a7f03b35dcb0c361cf1e578a3930697524b0edeb  iris.csv
```

## How to cite

Fisher, R. A. (1936). *Iris* [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C56C76

Fisher, R. A. (1936). The use of multiple measurements in taxonomic
problems. *Annals of Eugenics*, 7(2), 179–188.
https://doi.org/10.1111/j.1469-1809.1936.tb02137.x
