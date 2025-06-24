from pyspark.sql import SparkSession
from pyspark.sql.functions import col, collect_list, struct, udf, array_join
from pyspark.sql.types import ArrayType, StringType, StructType, StructField
from pyspark.ml.feature import Word2Vec
import os
import numpy as np
import sys
from collections import defaultdict

#自己的Java环境变量，最好用Java 17版本
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-17'
os.environ['PATH'] = os.environ['JAVA_HOME'] + r'\bin;' + os.environ.get('PATH', '')

python_path = sys.executable
os.environ['PYSPARK_PYTHON'] = python_path
os.environ['PYSPARK_DRIVER_PYTHON'] = python_path

print(f"Using Python: {python_path}")
print(f"Python version: {sys.version}")

class Embedding:
    def __init__(self):
        """初始化Spark会话"""
        print(f"Using Java from: {os.environ.get('JAVA_HOME', 'Not set')}")
        
        self.spark = SparkSession.builder \
            .appName("MovieEmbedding") \
            .master("local[*]") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
            .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true") \
            .config("spark.python.worker.faulthandler.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.shuffle.partitions", "8") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
    
    def process_item_sequence(self, ratings_path):
        print(f"Reading ratings data from: {ratings_path}")
        
        ratings_df = self.spark.read.format("csv") \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .load(ratings_path)
        
        print("Ratings schema:")
        ratings_df.printSchema()
        
        print(f"Total ratings count: {ratings_df.count()}")
        
        print("Filtering ratings >= 3.5 and sorting by user and timestamp...")
        high_ratings = ratings_df.filter(col("rating") >= 3.5) \
            .select("userId", "movieId", "timestamp") \
            .orderBy("userId", "timestamp")
        
        print(f"High ratings count: {high_ratings.count()}")
        
        print("Collecting data for local processing...")
        ratings_data = high_ratings.collect()
        print(f"Collected {len(ratings_data)} high rating records")
        
        if not ratings_data:
            raise ValueError("No rating data collected")
        
        print("Processing user sequences locally...")
        user_sequences = defaultdict(list)
        
        for row in ratings_data:
            user_id = row.userId
            movie_id = str(row.movieId)  
            user_sequences[user_id].append(movie_id)
        
        valid_sequences = []
        for user_id in sorted(user_sequences.keys()):  
            movies = user_sequences[user_id]
            if len(movies) > 1:
                valid_sequences.append(movies)
        
        print(f"Generated {len(valid_sequences)} valid user sequences")
        
        print("Sample sequences:")
        for i, seq in enumerate(valid_sequences[:3]):
            print(f"  User sequence {i+1}: {seq[:10]}...")
        
        return valid_sequences
    
    def train_item2vec(self, sequences, emb_length=10, emb_output_filename="item2vecEmb.csv"):
        print(f"Training Word2Vec model with embedding length: {emb_length}")
        
        if not sequences:
            raise ValueError("No sequences available for training")
        
        print(f"Training with {len(sequences)} sequences")
        
        total_movies = set()
        for seq in sequences:
            total_movies.update(seq)
        print(f"Total unique movies in sequences: {len(total_movies)}")
        
        try:
            schema = StructType([StructField("sequence", ArrayType(StringType()), True)])
            sequences_df = self.spark.createDataFrame(
                [(seq,) for seq in sequences], 
                schema
            )
            
            print(f"Created DataFrame with {sequences_df.count()} sequences")
            
            word2vec = Word2Vec(
                vectorSize=emb_length,
                windowSize=5,
                inputCol="sequence",
                outputCol="vectors",
                minCount=1,  
                maxIter=1,   
                stepSize=0.025,
                seed=42      
            )
            
            print("Training Word2Vec model...")
            model = word2vec.fit(sequences_df)
            
            vectors_df = model.getVectors()
            vectors_count = vectors_df.count()
            print(f"Generated embeddings for {vectors_count} movies")
            
            if vectors_count > 0:
                print("Sample movie embeddings:")
                sample_vectors = vectors_df.orderBy("word").limit(5)
                sample_vectors.show(truncate=False)
            
            output_dir = "data/modeldata"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, emb_output_filename)
            
            print(f"Saving item embeddings to: {output_path}")
            vectors_data = vectors_df.orderBy("word").collect()  
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for row in vectors_data:
                    movie_id = row.word
                    vector = row.vector.toArray()
                    vector_str = ' '.join([f"{v:.6f}" for v in vector])
                    f.write(f"{movie_id}:{vector_str}\n")
            
            print(f"Item embeddings saved to {output_path}")
            
            with open(output_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"Saved {len(lines)} movie embeddings")
                if lines:
                    print(f"First embedding: {lines[0].strip()}")
            
            return model
            
        except Exception as e:
            print(f"Error in Word2Vec training: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_user_emb(self, ratings_path, word2vec_model, emb_length=10, emb_output_filename="userEmb.csv"):
        print("Generating user embeddings...")
        
        output_dir = "data/modeldata"
        item_emb_path = os.path.join(output_dir, "item2vecEmb.csv")
        
        movie_vectors = {}
        if os.path.exists(item_emb_path):
            print(f"Loading item embeddings from: {item_emb_path}")
            with open(item_emb_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        parts = line.split(':', 1)
                        movie_id = parts[0]
                        vector_str = parts[1]
                        try:
                            vector = np.array([float(x) for x in vector_str.split()])
                            movie_vectors[movie_id] = vector
                        except ValueError as e:
                            print(f"Error parsing vector for movie {movie_id}: {e}")
        else:
            print(f"Item embeddings file not found: {item_emb_path}")
            return
        
        print(f"Loaded {len(movie_vectors)} movie vectors")
        
        ratings_df = self.spark.read.format("csv") \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .load(ratings_path)
        
        print("Collecting ratings data for user embedding generation...")
        ratings_data = ratings_df.collect()
        user_embeddings = {}
        user_movies = defaultdict(list)
        
        for row in ratings_data:
            user_id = str(row.userId)
            movie_id = str(row.movieId)
            user_movies[user_id].append(movie_id)
        
        print(f"Processing {len(user_movies)} users")
        
        users_with_embeddings = 0
        for user_id in sorted(user_movies.keys()):  
            movies = user_movies[user_id]
            user_emb = np.zeros(emb_length, dtype=np.float64)
            valid_movies = 0
            
            for movie_id in movies:
                if movie_id in movie_vectors:
                    user_emb += movie_vectors[movie_id]
                    valid_movies += 1
            
            if valid_movies > 0:
                user_emb = user_emb / valid_movies  
                user_embeddings[user_id] = user_emb
                users_with_embeddings += 1
        
        print(f"Generated embeddings for {users_with_embeddings} users")
        
        output_path = os.path.join(output_dir, emb_output_filename)
        print(f"Saving user embeddings to: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for user_id in sorted(user_embeddings.keys()):  
                embedding = user_embeddings[user_id]
                vector_str = ' '.join([f"{v:.6f}" for v in embedding])
                f.write(f"{user_id}:{vector_str}\n")
        
        print(f"User embeddings saved to {output_path}")
        
        with open(output_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Saved {len(lines)} user embeddings")
            if lines:
                print(f"First user embedding: {lines[0].strip()}")
    
    def close(self):
        """关闭Spark session"""
        print("Closing Spark session...")
        self.spark.stop()

def main():
    """主函数"""
    print("=" * 60)
    print("Movie Embedding Training with PySpark")
    print("=" * 60)
    
    java_home = os.environ.get('JAVA_HOME')
    if not java_home:
        print("Warning: JAVA_HOME not set!")
    else:
        print(f"JAVA_HOME: {java_home}")
    embedding = None
    
    try:
        print("Initializing Spark session...")
        embedding = Embedding()
        
        base_path = r"C:\Users\86158\Desktop\数据库\SQL_HOMEWORK-master\data"
        ratings_path = os.path.join(base_path, "ratings.csv")
        
        emb_length = 10
        
        print(f"Checking for ratings file: {ratings_path}")
        if not os.path.exists(ratings_path):
            print(f"Error: {ratings_path} not found!")
            return
        
        print(f"Found ratings file: {ratings_path}")
        print(f"Embedding vector length: {emb_length}")
        
        print("\n" + "="*60)
        print("Step 1: Processing item sequences...")
        print("="*60)
        sequences = embedding.process_item_sequence(ratings_path)
        
        print("\n" + "="*60)
        print("Step 2: Training Word2Vec model...")
        print("="*60)
        model = embedding.train_item2vec(sequences, emb_length, "item2vecEmb.csv")
        
        if model is not None:
            print("\n" + "="*60)
            print("Step 3: Generating user embeddings...")
            print("="*60)
            embedding.generate_user_emb(ratings_path, model, emb_length, "userEmb.csv")
            
            print("\n" + "="*60)
            print("Embedding training failed!")
            print("="*60)
        else:
            print("Word2Vec training success!")
        
        output_dir = "data/modeldata"
        item_emb_path = os.path.join(output_dir, "item2vecEmb.csv")
        user_emb_path = os.path.join(output_dir, "userEmb.csv")
        
        print("Output files generated:")
        if os.path.exists(item_emb_path):
            print(f"✓ Movie embeddings: {item_emb_path}")
            existing_file = os.path.join("data", "item2vecEmb.csv")
            if os.path.exists(existing_file):
                print(f"  Comparing with existing file: {existing_file}")
        if os.path.exists(user_emb_path):
            print(f"✓ User embeddings: {user_emb_path}")
        
        try:
            if os.path.exists(item_emb_path):
                item_size = os.path.getsize(item_emb_path)
                print(f"  Item embeddings file size: {item_size / 1024:.2f} KB")
            
            if os.path.exists(user_emb_path):
                user_size = os.path.getsize(user_emb_path)
                print(f"  User embeddings file size: {user_size / 1024:.2f} KB")
        except Exception as e:
            print(f"Could not get file size info: {e}")
        
    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if embedding:
            embedding.close()

if __name__ == "__main__":
    main()