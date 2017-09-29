import math
import os
from pyspark.mllib.recommendation import ALS
from pyspark import SparkContext, SparkConf

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading Ratings data...")
sc = SparkContext()
dataset_path = os.path.join('../datasets', 'BX-CSV-Dump')
ratings_file_path = os.path.join(dataset_path, 'BX-Book-Ratings.csv')
ratings_raw_RDD = sc.textFile(ratings_file_path)
ratings_raw_data_header = ratings_raw_RDD.take(1)[0]
ratings_RDD = ratings_raw_RDD.filter(lambda line: line!=ratings_raw_data_header)\
    .map(lambda line: line.split(";"))\
    .map(lambda tokens: (int(tokens[0][1:-1]), abs(hash(tokens[1][1:-1])) % (10 ** 8), int(tokens[2][1:-1]))).cache()

test, train, validate = ratings_RDD.randomSplit(weights=[0.3, 0.6, 0.1], seed=1)

test = test.map(lambda token: (token[0], token[1]))

seed = 5L
iterations = 10
regularization_parameter = 0.1
ranks = [4, 8, 12, 16, 20]
errors = [0, 0, 0, 0, 0]
err = 0
tolerance = 0.02

min_error = float('inf')
best_rank = -1
best_iteration = -1
for rank in ranks:
    model = ALS.train(train, rank, seed=seed, iterations=iterations,
                      lambda_=regularization_parameter)
    predictions = model.predictAll(test).map(lambda r: ((r[0], r[1]), r[2]))
    rates_and_preds = validate.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
    error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
    errors[err] = error
    err += 1
    print 'For rank %s the RMSE is %s' % (rank, error)
    if error < min_error:
        min_error = error
        best_rank = rank

print 'The best model was trained with rank %s' % best_rank
