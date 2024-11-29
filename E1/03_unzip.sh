#! /bin/zsh -

tmp_fullpath=$1

cd $BASE_DATA_PATH"machine_learning" && \
  unzip -o reviews.zip && \
  tar -xvf *.tgz && \
  rm -vf *.tgz && \
  mv *.zip $tmp_fullpath && \
  cd ../..