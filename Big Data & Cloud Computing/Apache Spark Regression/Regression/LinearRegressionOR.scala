import org.apache.spark.ml.feature.{VectorAssembler, StringIndexer}
import org.apache.spark.ml.regression.LinearRegression

// Import data
val training = spark.read.options(Map("inferSchema"->"true","delimiter"->",","header"->"true")).csv("../data/OR.csv")

// Feature column
val featureCols = Array("In1",  "In2" )
val assembler = new VectorAssembler().setInputCols(featureCols).setOutputCol("features")
val training2 = assembler.transform(training)

// Label column
val labelIndexer = new StringIndexer().setInputCol("Out").setOutputCol("label")
val training3 = labelIndexer.fit(training2).transform(training2)

// Final Data
val data = training3.select($"features",$"label")

//Linear Regression Model
val lr = new LinearRegression().setMaxIter(10).setRegParam(0.3).setElasticNetParam(0.8)

// Fit the model
val lrModel = lr.fit(data)

// Print the coefficients and intercept for linear regression
println(s"Coefficients: ${lrModel.coefficients} Intercept: ${lrModel.intercept}")

// Summarize the model over the training set and print out some metrics
val trainingSummary = lrModel.summary
println(s"numIterations: ${trainingSummary.totalIterations}")
println(s"objectiveHistory: [${trainingSummary.objectiveHistory.mkString(",")}]")
trainingSummary.residuals.show()
println(s"RMSE: ${trainingSummary.rootMeanSquaredError}")
println(s"r2: ${trainingSummary.r2}")