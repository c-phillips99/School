import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.evaluation.RegressionEvaluator
import org.apache.spark.ml.regression.{RandomForestRegressionModel, RandomForestRegressor}
import org.apache.spark.ml.feature.{VectorAssembler, StringIndexer, VectorIndexer}

// Import data
val training = spark.read.options(Map("inferSchema"->"true","delimiter"->",","header"->"true")).csv("../data/sine.csv")

// Feature column
val featureCols = Array("In" )
val assembler = new VectorAssembler().setInputCols(featureCols).setOutputCol("features")
val training2 = assembler.transform(training)

// Label column
val labelIndexer = new StringIndexer().setInputCol("Out").setOutputCol("label")
val training3 = labelIndexer.fit(training2).transform(training2)

// Final Data
val data = training3.select($"features",$"label")

// Automatically identify categorical features, and index them.
// Set maxCategories so features with > 4 distinct values are treated as continuous.
val featureIndexer = new VectorIndexer().setInputCol("features").setOutputCol("indexedFeatures").setMaxCategories(4).fit(data)

// Split the data into training and test sets (30% held out for testing).
val Array(trainingData, testData) = data.randomSplit(Array(0.7, 0.3))

// Train a RandomForest model.
val rf = new RandomForestRegressor().setLabelCol("label").setFeaturesCol("indexedFeatures")

// Chain indexer and forest in a Pipeline.
val pipeline = new Pipeline().setStages(Array(featureIndexer, rf))

// Train model. This also runs the indexer.
val model = pipeline.fit(trainingData)

// Make predictions.
val predictions = model.transform(testData)

// Select example rows to display.
predictions.select("prediction", "label", "features").show(5)

// Select (prediction, true label) and compute test error.
val evaluator = new RegressionEvaluator().setLabelCol("label").setPredictionCol("prediction").setMetricName("rmse")
val rmse = evaluator.evaluate(predictions)
println(s"Root Mean Squared Error (RMSE) on test data = $rmse")

val rfModel = model.stages(1).asInstanceOf[RandomForestRegressionModel]
println(s"Learned regression forest model:\n ${rfModel.toDebugString}")