import org.apache.spark.ml.evaluation.RegressionEvaluator
import org.apache.spark.ml.feature.{VectorAssembler, StringIndexer}
import org.apache.spark.ml.regression.LinearRegression

// Import data
val training = spark.read.options(Map("inferSchema"->"true","delimiter"->",","header"->"true")).csv("../data/sine.csv")

// Feature column
val featureCols = Array("In")
val assembler = new VectorAssembler().setInputCols(featureCols).setOutputCol("features")
val training2 = assembler.transform(training)

// Label column
val labelIndexer = new StringIndexer().setInputCol("Out").setOutputCol("label")
val training3 = labelIndexer.fit(training2).transform(training2)

// Final Data
val data = training3.select($"features",$"label")
val Array(trainingData, testData) = data.randomSplit(Array(0.7, 0.3))

//Linear Regression Model
val lr = new LinearRegression().setMaxIter(10).setRegParam(0.3).setElasticNetParam(0.8)

// Fit the model
// val lrModel = lr.fit(data)
val lrModel = lr.fit(trainingData)
val predictions = lrModel.transform(testData)

// Select example rows to display.
predictions.select("predictedLabel", "label", "features").show(5)

// Select (prediction, true label) and compute test error.
val evaluator = new RegressionEvaluator().setLabelCol("label").setPredictionCol("prediction").setMetricName("rmse")
val rmse = evaluator.evaluate(predictions)
println(s"Root Mean Squared Error (RMSE) on test data = $rmse")
