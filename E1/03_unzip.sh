#! /bin/zsh -

cd data/machine_learning && \
  unzip -o reviews.zip amazon_review_polarity_csv.tgz && \
  tar -xvf amazon_review_polarity_csv.tgz && \
  rm -vf amazon_review_polarity_csv.tgz && \
  mv reviews.zip $tmp_fullpath && \
  cd ../..