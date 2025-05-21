sudo apt update

# OCR용 패키지 설치
pip install pytesseract
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-kor

# Mecab-ko 설치 (Ubuntu)
# wget https://bitbucket.org/eunjeon/mecab-ko/downloads/mecab-0.996-ko-0.9.2.tar.gz
# tar xvfz mecab-0.996-ko-0.9.2.tar.gz
# cd mecab-0.996-ko-0.9.2
# ./configure
# make
# make check
# sudo make install

# Mecab-dic 설치 (Ubuntu)
# wget https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.1.1-20180720.tar.gz
# tar xvfz mecab-ko-dic-2.1.1-20180720.tar.gz
# cd mecab-ko-dic-2.1.1-20180720
# ./configure
# make
# sudo make install

# Mecab-dic이 존재하지 않는다는 에러 발생 시
# sudo mkdir -p /usr/local/lib/mecab/dic
# sudo ln -s /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ko-dic /usr/local/lib/mecab/dic/mecab-ko-dic