# PyDeequ

PyDeequ is a Python API for [Deequ](https://github.com/awslabs/deequ), a library built on top of Apache Spark for defining "unit tests for data", which measure data quality in large datasets. PyDeequ is written to support usage of Deequ in Python.

[![CodeQL](https://github.com/ChethanUK/pydeequ3/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/ChethanUK/pydeequ3/actions/workflows/codeql-analysis.yml) [![BuildAndTest](https://github.com/ChethanUK/pydeequ3/actions/workflows/build_test.yml/badge.svg)](https://github.com/ChethanUK/pydeequ3/actions/workflows/build_test.yml) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/ChethanUK/pydeequ3.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/ChethanUK/pydeequ3/context:python)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)



There are 4 main components of Deequ, and they are:

- Metrics Computation:
  - `Profiles` leverages Analyzers to analyze each column of a dataset.
  - `Analyzers` serve here as a foundational module that computes metrics for data profiling and validation at scale.
- Constraint Suggestion:
  - Specify rules for various groups of Analyzers to be run over a dataset to return back a collection of constraints suggested to run in a Verification Suite.
- Constraint Verification:
  - Perform data validation on a dataset with respect to various constraints set by you.
- Metrics Repository
  - Allows for persistence and tracking of Deequ runs over time.

![](imgs/pydeequ_architecture.jpg)

## 🎉 Announcements 🎉

We've release a blogpost on integrating PyDeequ onto AWS leveraging services such as AWS Glue, Athena, and SageMaker! Check it out: [Monitor data quality in your data lake using PyDeequ and AWS Glue](https://aws.amazon.com/blogs/big-data/monitor-data-quality-in-your-data-lake-using-pydeequ-and-aws-glue/).

## Quickstart

The following will quickstart you with some basic usage. For more in-depth examples, take a look in the [`tutorials/`](tutorials/) directory for executable Jupyter notebooks of each module. For documentation on supported interfaces, view the [`documentation`](https://pydeequ.readthedocs.io/).

### Installation

You can install [PyDeequ via pip](https://pypi.org/project/pydeequ/).

```bash
pip install pydeequ3
```

### Set up a PySpark session

```python
from pyspark.sql import SparkSession, Row
import pydeequ3 as pydeequ

spark = (SparkSession
    .builder
    .config("spark.jars.packages", pydeequ.deequ_maven_coord)
    .config("spark.jars.excludes", pydeequ.f2j_maven_coord)
    .getOrCreate())

df = spark.sparkContext.parallelize([
            Row(a="foo", b=1, c=5),
            Row(a="bar", b=2, c=6),
            Row(a="baz", b=3, c=None)]).toDF()
```

### Analyzers

```python
try:
    from pydeequ.analyzers import *
except Exception:
    from pydeequ3.analyzers import *

analysisResult = AnalysisRunner(spark) \
                    .onData(df) \
                    .addAnalyzer(Size()) \
                    .addAnalyzer(Completeness("b")) \
                    .run()

analysisResult_df = AnalyzerContext.successMetricsAsDataFrame(spark, analysisResult)
analysisResult_df.show()
```

### Profile

```python
try:
    from pydeequ.profiles import *
except Exception:
    from pydeequ3.profiles import *

result = ColumnProfilerRunner(spark) \
    .onData(df) \
    .run()

for col, profile in result.profiles.items():
    print(profile)
```

### Constraint Suggestions

```python
try:
    from pydeequ.suggestions import *
except Exception:
    from pydeequ3.suggestions import *

suggestionResult = ConstraintSuggestionRunner(spark) \
             .onData(df) \
             .addConstraintRule(DEFAULT()) \
             .run()

# Constraint Suggestions in JSON format
print(suggestionResult)
```

### Constraint Verification

```python
try:
    from pydeequ.checks import *
    from pydeequ.verification import *
except Exception:
    from pydeequ3.checks import *
    from pydeequ3.verification import *


check = Check(spark, CheckLevel.Warning, "Review Check")

checkResult = VerificationSuite(spark) \
    .onData(df) \
    .addCheck(
        check.hasSize(lambda x: x >= 3) \
        .hasMin("b", lambda x: x == 0) \
        .isComplete("c")  \
        .isUnique("a")  \
        .isContainedIn("a", ["foo", "bar", "baz"]) \
        .isNonNegative("b")) \
    .run()

checkResult_df = VerificationResult.checkResultsAsDataFrame(spark, checkResult)
checkResult_df.show()
```

### Repository

Save to a Metrics Repository by adding the `useRepository()` and `saveOrAppendResult()` calls to your Analysis Runner.

```python
try:
    from pydeequ.repository import *
    from pydeequ.analyzers import *
except Exception:
    from pydeequ3.repository import *
    from pydeequ3.analyzers import *


metrics_file = FileSystemMetricsRepository.helper_metrics_file(spark, 'metrics.json')
repository = FileSystemMetricsRepository(spark, metrics_file)
key_tags = {'tag': 'pydeequ hello world'}
resultKey = ResultKey(spark, ResultKey.current_milli_time(), key_tags)

analysisResult = AnalysisRunner(spark) \
    .onData(df) \
    .addAnalyzer(ApproxCountDistinct('b')) \
    .useRepository(repository) \
    .saveOrAppendResult(resultKey) \
    .run()
```

To load previous runs, use the `repository` object to load previous results back in.

```python
result_metrep_df = repository.load() \
    .before(ResultKey.current_milli_time()) \
    .forAnalyzers([ApproxCountDistinct('b')]) \
    .getSuccessMetricsAsDataFrame()
```

## [Contributing](https://github.com/awslabs/python-deequ/blob/master/CONTRIBUTING.md)

Setup dev environment:

- Install [Python](https://github.com/pyenv/pyenv#homebrew-on-macos):

Example:

```bash
pyenv install 3.8.5
pyenv local 3.8.5
```

- Install [Poetry](https://python-poetry.org/docs/#osx-linux-bashonwindows-install-instructions)

- Install pre-commit hooks:

```bash
pre-commit install --install-hooks
```

- Once you made you changes, run the pre-commit run and make sure all stages are passing:

```bash
pre-commit run -a

Check for case conflicts.................................................Passed
Check for merge conflicts................................................Passed
Check for added large files..............................................Passed
... etc...
```

Then, Please refer to the [contributing doc](https://github.com/awslabs/python-deequ/blob/master/CONTRIBUTING.md) for how to contribute to PyDeequ.

## [License](https://github.com/awslabs/python-deequ/blob/master/LICENSE)

This library is licensed under the Apache 2.0 License.
