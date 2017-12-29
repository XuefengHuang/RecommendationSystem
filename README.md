# spark-book-recommender-system
## 项目简介
* 基于Spark, Python Flask, 和 [Book-Crossing Dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/) 的在线图书推荐系统。
* 该图书推荐系统参考https://github.com/jadianes/spark-movie-lens。
* 修改数据处理部分，使其支持[Book-Crossing Dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/)。
* 适合初学者学习如何搭建一个推荐系统，本文底下附有其他数据，可供参考学习。
* **如果觉得好，请给项目点颗星来支持吧～～**

## 基于模型的[协同过滤](https://xuefenghuang.github.io/collaborate-filter/)应用---图书推荐
本文实现对用户推荐图书的简单应用。
* 1. 推荐算法：

在我们的在线图书推荐系统中，我们借用Spark的ALS算法的训练和预测函数，每次收到新的数据后，将其更新到训练数据集中，然后更新ALS训练得到的模型。

假设我们有一组用户，他们表现出了对一组图书的喜好。用户对一本图书的喜好程度越高，就会给其更高的评分，范围是从1到5。我们来通过一个矩阵来展示它，行代表用户，列代表图书。用户对图书的评分。所有的评分范围从1到5，5代表喜欢程度最高。第一个用户（行1）对第一个图书（列1）的评分是4。空的单元格代表用户未给图书评价。

![Image of Example1](https://github.com/XuefengHuang/spark-book-recommender-system/blob/master/images/example1.png)

矩阵因子分解（如奇异值分解，奇异值分解+ +）将项和用户都转化成了相同的潜在空间，它所代表了用户和项之间的潜相互作用。矩阵分解背后的原理是潜在特征代表了用户如何给项进行评分。给定用户和项的潜在描述，我们可以预测用户将会给还未评价的项多少评分。

![Image of Example1](https://github.com/XuefengHuang/spark-book-recommender-system/blob/master/images/example2.png)

* 2. 数据描述：
评分数据文件:

`"User-ID";"ISBN";"Book-Rating"`

```
"276725";"034545104X";"0"
"276726";"0155061224";"5"
"276727";"0446520802";"0"
"276729";"052165615X";"3"
"276729";"0521795028";"6"
"276733";"2080674722";"0"
"276736";"3257224281";"8"
```

图书数据文件:

`"ISBN";"Book-Title";"Book-Author";"Year-Of-Publication";"Publisher";"Image-URL-S";"Image-URL-M";"Image-URL-L"`

```
"0195153448";"Classical Mythology";"Mark P. O. Morford";"2002";"Oxford University Press";"http://images.amazon.com/images/P/0195153448.01.THUMBZZZ.jpg";"http://images.amazon.com/images/P/0195153448.01.MZZZZZZZ.jpg";"http://images.amazon.com/images/P/0195153448.01.LZZZZZZZ.jpg"
"0002005018";"Clara Callan";"Richard Bruce Wright";"2001";"HarperFlamingo Canada";"http://images.amazon.com/images/P/0002005018.01.THUMBZZZ.jpg";"http://images.amazon.com/images/P/0002005018.01.MZZZZZZZ.jpg";"http://images.amazon.com/images/P/0002005018.01.LZZZZZZZ.jpg"
"0060973129";"Decision in Normandy";"Carlo D'Este";"1991";"HarperPerennial";"http://images.amazon.com/images/P/0060973129.01.THUMBZZZ.jpg";"http://images.amazon.com/images/P/0060973129.01.MZZZZZZZ.jpg";"http://images.amazon.com/images/P/0060973129.01.LZZZZZZZ.jpg"
"0374157065";"Flu: The Story of the Great Influenza Pandemic of 1918 and the Search for the Virus That Caused It";"Gina Bari Kolata";"1999";"Farrar Straus Giroux";"http://images.amazon.com/images/P/0374157065.01.THUMBZZZ.jpg";"http://images.amazon.com/images/P/0374157065.01.MZZZZZZZ.jpg";"http://images.amazon.com/images/P/0374157065.01.LZZZZZZZ.jpg"
"0393045218";"The Mummies of Urumchi";"E. J. W. Barber";"1999";"W. W. Norton &amp; Company";"http://images.amazon.com/images/P/0393045218.01.THUMBZZZ.jpg";"http://images.amazon.com/images/P/0393045218.01.MZZZZZZZ.jpg";"http://images.amazon.com/images/P/0393045218.01.LZZZZZZZ.jpg"
```

* 3. 数据处理细节：

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

* 4. 选择模型参数：
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

* 5. 模型保存
```
from pyspark.mllib.recommendation import MatrixFactorizationModel

model_path = os.path.join('..', 'models', 'book_als')

# Save and load model
model.save(sc, model_path)
same_model = MatrixFactorizationModel.load(sc, model_path)
```

* 6. 运行说明：
```
virtualenv book
pip install -r requirements.txt
python server.py
```

* 7. API:
```
GET: /<int:user_id>/ratings/top/<int:count> 获取用户图书推荐top N信息
GET: /<int:user_id>/ratings/<string:book_id> 获取该用户对某个图书的评价信息
POST: /<int:user_id>/ratings 新增图书评价信息
```

* 8. 接口调用示例：


```
GET: /276729/ratings/top/3 获取用户ID为276729的图书推荐top3信息
返回信息：

[
  {
    "Count": 30,
    "Rating": 8.781754720405482,
    "Author": "MARJANE SATRAPI",
    "URL": "http://images.amazon.com/images/P/0375422307.01.THUMBZZZ.jpg",
    "Publisher": "Pantheon",
    "Title": "Persepolis : The Story of a Childhood (Alex Awards (Awards))",
    "Year": "2003"
  },
  {
    "Count": 31,
    "Rating": 7.093566643463471,
    "Author": "Stephen King",
    "URL": "http://images.amazon.com/images/P/067081458X.01.THUMBZZZ.jpg",
    "Publisher": "Viking Books",
    "Title": "The Eyes of the Dragon",
    "Year": "1987"
  },
  {
    "Count": 25,
    "Rating": 7.069147186199548,
    "Author": "Jean Sasson",
    "URL": "http://images.amazon.com/images/P/0967673747.01.THUMBZZZ.jpg",
    "Publisher": "Windsor-Brooke Books",
    "Title": "Princess: A True Story of Life Behind the Veil in Saudi Arabia",
    "Year": "2001"
  }
]
```

```
GET: /276729/ratings/0446520802 获取用户276729对图书(ISBN:0446520802)的评价信息
返回信息：

[
  {
    "Count": 116,
    "Rating": 1.4087434932956826,
    "Author": "Nicholas Sparks",
    "URL": "http://images.amazon.com/images/P/0446520802.01.THUMBZZZ.jpg",
    "Publisher": "Warner Books",
    "Title": "The Notebook",
    "Year": "1996"
  }
]
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
