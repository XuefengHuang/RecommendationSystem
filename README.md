# spark-book-recommender-system
* 基于Spark, Python Flask, 和[Book-Crossing Dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/)的在线图书推荐系统。
* 该图书推荐系统参考https://github.com/jadianes/spark-movie-lens。
* 修改数据处理部分，使其支持[Book-Crossing Dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/)。

* 运行说明：
```
virtualenv book
pip install -r requirements.txt
python server.py
```

* API:
```
GET: /<int:user_id>/ratings/top/<int:count> 获取用户图书推荐top N信息
GET: /<int:user_id>/ratings/<string:book_id> 获取该用户对某个图书的评价信息
POST: /<int:user_id>/ratings 新增图书评价信息
```
