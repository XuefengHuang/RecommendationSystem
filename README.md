# spark-book-recommender-system
## 项目简介
* 基于Spark, Python Flask, 和[Book-Crossing Dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/)的在线图书推荐系统。
* 该图书推荐系统参考https://github.com/jadianes/spark-movie-lens。
* 修改数据处理部分，使其支持[Book-Crossing Dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/)。
* 适合初学者学习如何搭建一个推荐系统，本文底下附有其他数据，可供参考学习。


## 协同过滤算法概述
通常，协同过滤算法按照数据使用，可以分为：
* 1. 基于用户（UserCF）---基于用户相似性

基于用户的协同过滤，通过不同用户对物品的评分来评测用户之间的相似性，基于用户之间的相似性做出推荐。简单来讲，就是给用户推荐和他兴趣相似的其他用户喜欢的物品。
* 2. 基于商品（ItemCF）---基于商品相似性

基于商品的协同过滤，通过用户对不同item的评分来评测item之间的相似性，基于item之间的相似性做出推荐。简单来将，就是给用户推荐和他之前喜欢的物品相似的物品。
* 3. 基于模型（ModelCF）

基于模型的协同过滤推荐就是基于样本的用户喜好信息，训练一个推荐模型，然后根据实时的用户喜好的信息进行预测，计算推荐。

![Image of ALS](https://github.com/XuefengHuang/spark-book-recommender-system/blob/master/images/ALS_Image_Test.png)

Spark MLlib当前支持基于模型的协同过滤，其中用户和商品通过一小组隐性因子进行表达，并且这些因子也用于预测缺失的元素。MLlib使用交替最小二乘法（ALS）来学习这些隐性因子。

我们先通过例子来看一下基于模型的协同过滤：

## 基于模型的协同过滤应用---图书推荐

本文实现对用户推荐图书的简单应用。
假设我们有一组用户，他们表现出了对一组图书的喜好。用户对一本图书的喜好程度越高，就会给其更高的评分，范围是从1到5。我们来通过一个矩阵来展示它，行代表用户，列代表图书。用户对图书的评分。所有的评分范围从1到5，5代表喜欢程度最高。第一个用户（行1）对第一个图书（列1）的评分是4。空的单元格代表用户未给图书评价。

![Image of Example1](https://github.com/XuefengHuang/spark-book-recommender-system/blob/master/images/example1.png)

基于模型的方法不像基于邻域的方法，使用用户项评分直接预测新的项。基于模型的方法会在使用评分去学习预测模型的基础上，去预测新项。一般的想法是使用机器学习算法建立用户和项的相互作用模型，从而找出数据中的模式。在一般情况下，基于模型的CF被认为是建立CF推荐系统的更先进的算法。有许多不同的算法可用于构建模型并基于这些模型进行预测，例如，贝叶斯网络、聚类、分类、回归、矩阵分解、受限玻尔兹曼机等等。这些技术在为了最终赢得Netflix奖的解决方案中扮演了关键角色。Netflix发起了一个竞赛，从2006年到2009年提供一百万美元奖金，颁发给产生的推荐比他们自己的推荐系统精确10%以上的推荐系统团队。成功获奖的解决方案是Netflix研发的一个集成（即混合）了超过100种算法模型，这些算法模型都采用了矩阵分解和受限玻尔兹曼机

矩阵因子分解（如奇异值分解，奇异值分解+ +）将项和用户都转化成了相同的潜在空间，它所代表了用户和项之间的潜相互作用。矩阵分解背后的原理是潜在特征代表了用户如何给项进行评分。给定用户和项的潜在描述，我们可以预测用户将会给还未评价的项多少评分。

![Image of Example1](https://github.com/XuefengHuang/spark-book-recommender-system/blob/master/images/example2.png)
* 1. 数据描述：

评分数据文件:

`"User-ID";"ISBN";"Book-Rating"`

图书数据文件:

`"ISBN";"Book-Title";"Book-Author";"Year-Of-Publication";"Publisher";"Image-URL-S";"Image-URL-M";"Image-URL-L"`

* 2. 数据处理细节：

由于该数据中ISBN为string格式，spark的ALS默认product id为int格式，因此对该ISBN号进行计算hash处理并取前8位防止整数越界。详细代码如下：

```
dataset_path = os.path.join('datasets', 'BX-CSV-Dump')
sc = SparkContext("local[*]", "Test")
ratings_file_path = os.path.join(dataset_path, 'BX-Book-Ratings.csv')
ratings_raw_RDD = sc.textFile(ratings_file_path)
ratings_raw_data_header = ratings_raw_RDD.take(1)[0]
ratings_RDD = ratings_raw_RDD.filter(lambda line: line!=ratings_raw_data_header)\
            .map(lambda line: line.split(";")).map(lambda tokens: (int(tokens[0][1:-1]), abs(hash(tokens[1][1:-1])) % (10 ** 8),float(tokens[2][1:-1]))).cache()

books_file_path = os.path.join(dataset_path, 'BX-Books.csv')
books_raw_RDD = sc.textFile(books_file_path)
books_raw_data_header = books_raw_RDD.take(1)[0]
books_RDD = books_raw_RDD.filter(lambda line: line!=books_raw_data_header)\
    .map(lambda line: line.split(";"))\
    .map(lambda tokens: (abs(hash(tokens[0][1:-1])) % (10 ** 8), tokens[1][1:-1], tokens[2][1:-1], tokens[3][1:-1], tokens[4][1:-1], tokens[5][1:-1])).cache()
books_titles_RDD = books_RDD.map(lambda x: (int(x[0]), x[1], x[2], x[3], x[4], x[5])).cache()
```

* 3. 选择模型参数：
```
from pyspark.mllib.recommendation import ALS
import math

seed = 5L
iterations = 10
regularization_parameter = 0.1
ranks = [4, 8, 12]
errors = [0, 0, 0]
err = 0
tolerance = 0.02

min_error = float('inf')
best_rank = -1
best_iteration = -1
for rank in ranks:
    model = ALS.train(training_RDD, rank, seed=seed, iterations=iterations,
                      lambda_=regularization_parameter)
    predictions = model.predictAll(validation_for_predict_RDD).map(lambda r: ((r[0], r[1]), r[2]))
    rates_and_preds = validation_RDD.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
    error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
    errors[err] = error
    err += 1
    print 'For rank %s the RMSE is %s' % (rank, error)
    if error < min_error:
        min_error = error
        best_rank = rank

print 'The best model was trained with rank %s' % best_rank
```

* 4. 模型保存
```
from pyspark.mllib.recommendation import MatrixFactorizationModel

model_path = os.path.join('..', 'models', 'book_als')

# Save and load model
model.save(sc, model_path)
same_model = MatrixFactorizationModel.load(sc, model_path)
```

* 5. 运行说明：
```
virtualenv book
pip install -r requirements.txt
python server.py
```

* 6. API:
```
GET: /<int:user_id>/ratings/top/<int:count> 获取用户图书推荐top N信息
GET: /<int:user_id>/ratings/<string:book_id> 获取该用户对某个图书的评价信息
POST: /<int:user_id>/ratings 新增图书评价信息
```

## 其他数据集推荐（参考https://gist.github.com/entaroadun/1653794）

以下数据可以提供给初学者学习如何训练推荐算法模型

**电影数据**:

* *MovieLens* - Movie Recommendation Data Sets http://www.grouplens.org/node/73
* *Yahoo!* - Movie, Music, and Images Ratings Data Sets http://webscope.sandbox.yahoo.com/catalog.php?datatype=r
* *Cornell University* - Movie-review data for use in sentiment-analysis experiments http://www.cs.cornell.edu/people/pabo/movie-review-data/

**音乐数据**:

* *Last.fm* - Music Recommendation Data Sets http://www.dtic.upf.edu/~ocelma/MusicRecommendationDataset/index.html
* *Yahoo!* - Movie, Music, and Images Ratings Data Sets http://webscope.sandbox.yahoo.com/catalog.php?datatype=r
* *Audioscrobbler* - Music Recommendation Data Sets http://www-etud.iro.umontreal.ca/~bergstrj/audioscrobbler_data.html
* *Amazon* - Audio CD recommendations http://131.193.40.52/data/


**图书数据**:

* *Institut für Informatik, Universität Freiburg* - Book Ratings Data Sets http://www.informatik.uni-freiburg.de/~cziegler/BX/


**美食数据**:

* *Chicago Entree* - Food Ratings Data Sets http://archive.ics.uci.edu/ml/datasets/Entree+Chicago+Recommendation+Data


**商品数据**:

* *Amazon* - Product Recommendation Data Sets http://131.193.40.52/data/


**健康数据**:

* *Nursing Home* - Provider Ratings Data Set http://data.medicare.gov/dataset/Nursing-Home-Compare-Provider-Ratings/mufm-vy8d
* *Hospital Ratings* - Survey of Patients Hospital Experiences http://data.medicare.gov/dataset/Survey-of-Patients-Hospital-Experiences-HCAHPS-/rj76-22dk


**相亲数据**:

* *www.libimseti.cz* - Dating website recommendation (collaborative filtering) http://www.occamslab.com/petricek/data/


**学术文章推荐**:

* *National University of Singapore* - Scholarly Paper Recommendation http://www.comp.nus.edu.sg/~sugiyama/SchPaperRecData.html