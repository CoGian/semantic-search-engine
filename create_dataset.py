import langdetect as langdetect
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
import re
langdetect.DetectorFactory.seed = 0


@F.udf(returnType=StringType())
def process_text(text):
    proc_text = text.lower()
    proc_text = re.sub("\n", " ", proc_text)
    proc_text = re.sub("\t", " ", proc_text)
    proc_text = re.sub('\r', '', proc_text)
    proc_text = re.sub('\$.*?\$', '', proc_text)
    proc_text = re.sub('<.*?>', '', proc_text)
    proc_text = re.sub('\s+', ' ', proc_text)
    proc_text = " ".join(proc_text.split())
    return proc_text


# language filter function
@F.udf(returnType=BooleanType())
def lang_filter(col):
	try:
		return langdetect.detect(col) == "en"
	except langdetect.LangDetectException:
		return False


if __name__ == '__main__':

	spark = SparkSession.Builder().master("local[*]")\
		.config("spark.driver.memory", "8g").getOrCreate()

	s2orc_dataset = spark.read.json("data/*.gz")

	s2orc_dataset_filtered = s2orc_dataset.filter(F.col("pdfUrls").getItem(0).contains("arxiv"))\
			.filter(F.col("paperAbstract").isNotNull())\
			.filter(lang_filter("title"))

	s2orc_dataset_filtered.select(
		'authors',
		'doi',
		'fieldsOfStudy',
		'id',
		'journalName',
		process_text('title').alias('title'),
		process_text('paperAbstract').alias('paperAbstract'),
		'year',
		'venue',
		F.col('pdfUrls').getItem(0).alias('pdfUrl'),
	).coalesce(1).write.json('dataset', mode='overwrite')






