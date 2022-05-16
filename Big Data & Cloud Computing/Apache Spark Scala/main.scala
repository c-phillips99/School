import org.apache.spark.sql.SparkSession


val spark = SparkSession.builder().appName("StudentExams").getOrCreate()
//import spark.implicits._

//Reading in JSON
val df1 = spark.read.json("StudentRecords.json")
val df2 = spark.read.json("Exams.json")

// Formatting df2 so that the collections are visible
val exam1 = df2.select(explode(df2("Exam 1"))).toDF("Exam 1")
val exam1c = exam1.select("Exam 1.Name", "Exam 1.Score")
val exam1f = exam1c.withColumn("Exam", lit ("Exam 1"))
val exam2 = df2.select(explode(df2("Exam 2"))).toDF("Exam 2")
val exam2c = exam2.select("Exam 2.Name", "Exam 2.Score")
val exam2f = exam2c.withColumn("Exam", lit ("Exam 2"))
val exam3 = df2.select(explode(df2("Exam 3"))).toDF("Exam 3")
val exam3c = exam3.select("Exam 3.Name", "Exam 3.Score")
val exam3f = exam3c.withColumn("Exam", lit ("Exam 3"))

// Creating SQL temporary views
df1.createOrReplaceTempView("students")
exam1f.createOrReplaceTempView("exam1")
exam2f.createOrReplaceTempView("exam2")
exam3f.createOrReplaceTempView("exam3")
spark.sql("SELECT * FROM exam1 UNION SELECT * FROM exam2 UNION SELECT * FROM exam3").createOrReplaceTempView("exams")

println ("Displaying all the distinct majors")
spark.sql("SELECT DISTINCT Major FROM students").show()

println ("\n\nDisplaying all the male students and their majors")
spark.sql("SELECT * FROM students WHERE Gender='Male'").show()

println ("\n\nDisplaying the average ages for male and female students respectively")
spark.sql("SELECT AVG(Age) FROM students GROUP BY Gender ORDER BY AVG(Age) ASC").show()

println ("\n\nDisplaying the students' names whose ages are under 22")
spark.sql("SELECT Name FROM students WHERE Age<22").show()

println ("\n\nDisplaying the student table, with ages sorted in descending order")
spark.sql("SELECT * FROM students ORDER BY Age DESC").show()

println ("\n\nDisplaying the average score for each exam")
spark.sql("SELECT AVG(Score), Exam FROM exams GROUP BY Exam ORDER BY Exam ASC").show()

println ("\n\nDisplaying the maximum and minimum score from all three exams and the student names who received these scores")
spark.sql("SELECT Score, Name, Exam from exams WHERE Score = (SELECT MIN(Score) FROM exams) OR Score = (SELECT MAX(Score) from exams) ORDER BY Exam ASC").show()

println ("\n\nDisplaying each exam, with scores sorted in descending order")
spark.sql("SELECT * from exams ORDER BY Exam, Score DESC").show()