import Crawler
import Preprocessor

if __name__ == "__main__":
    Crawler.crawl_skku_notices()
    Preprocessor.apply_preprocess()