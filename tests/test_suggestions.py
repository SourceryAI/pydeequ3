# -*- coding: utf-8 -*-
import json
import unittest

from pyspark.sql import Row, SparkSession

from pydeequ.suggestions import (
    DEFAULT,
    CategoricalRangeRule,
    CompleteIfCompleteRule,
    ConstraintSuggestionRunner,
    FractionalCategoricalRangeRule,
    NonNegativeNumbersRule,
    RetainCompletenessRule,
    RetainTypeRule,
    UniqueIfApproximatelyUniqueRule,
)


class TestSuggestions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        deequ_maven_coord = "com.amazon.deequ:deequ:1.2.2-spark-3.0"
        # This package is excluded because it causes an error in the SparkSession fig
        f2j_maven_coord = "net.sourceforge.f2j:arpack_combined_all"
        cls.spark = (
            SparkSession.builder.master("local[*]")
            .config("spark.jars.packages", deequ_maven_coord)
            .config("spark.pyspark.python", "/usr/bin/python3")
            .config("spark.pyspark.driver.python", "/usr/bin/python3")
            .config("spark.jars.excludes", f2j_maven_coord)
            .config("spark.driver.extraJavaOptions", "-XX:+UseG1GC")
            .config("spark.executor.extraJavaOptions", "-XX:+UseG1GC")
            .config("spark.sql.autoBroadcastJoinThreshold", "-1")
            .appName("test-analyzers-local")
            .getOrCreate()
        )
        cls.ConstraintSuggestionRunner = ConstraintSuggestionRunner(cls.spark)
        cls.sc = cls.spark.sparkContext
        cls.df = cls.sc.parallelize([Row(a="foo", b=1, c=5), Row(a="bar", b=2, c=6), Row(a="baz", b=3, c=None)]).toDF()

    @classmethod
    def tearDownClass(cls):
        cls.spark.sparkContext._gateway.shutdown_callback_server()
        cls.spark.stop()

    def test_CategoricalRangeRule(self):
        result = self.ConstraintSuggestionRunner.onData(self.df).addConstraintRule(CategoricalRangeRule()).run()
        print(json.dumps(result, indent=1))

    def test_CompleteIfCompleteRule(self):
        result = self.ConstraintSuggestionRunner.onData(self.df).addConstraintRule(CompleteIfCompleteRule()).run()
        print(json.dumps(result, indent=1))

    def test_FractionalCategoricalRangeRule(self):
        result = (
            self.ConstraintSuggestionRunner.onData(self.df).addConstraintRule(FractionalCategoricalRangeRule()).run()
        )
        print(json.dumps(result, indent=1))

    def test_NonNegativeNumbersRule(self):
        result = self.ConstraintSuggestionRunner.onData(self.df).addConstraintRule(NonNegativeNumbersRule()).run()
        print(json.dumps(result, indent=1))

    def test_RetainCompletenessRule(self):
        result = self.ConstraintSuggestionRunner.onData(self.df).addConstraintRule(RetainCompletenessRule()).run()
        print(json.dumps(result, indent=1))

    def test_RetainTypeRule(self):
        result = self.ConstraintSuggestionRunner.onData(self.df).addConstraintRule(RetainTypeRule()).run()
        print(json.dumps(result, indent=1))

    def test_UniqueIfApproximatelyUniqueRule(self):
        result = (
            self.ConstraintSuggestionRunner.onData(self.df).addConstraintRule(UniqueIfApproximatelyUniqueRule()).run()
        )
        print(json.dumps(result, indent=1))

    def test_default(self):
        result = self.ConstraintSuggestionRunner.onData(self.df).addConstraintRule(DEFAULT()).run()
        print(json.dumps(result, indent=1))
